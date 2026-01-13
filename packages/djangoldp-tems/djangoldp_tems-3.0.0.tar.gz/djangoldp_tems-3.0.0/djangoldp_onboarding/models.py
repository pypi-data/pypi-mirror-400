import logging
import re

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
# Email imports
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.loader import get_template
from django.utils.html import strip_tags
from django.utils.text import slugify
from djangoldp.permissions import (AuthenticatedOnly, CreateOnly,
                                   LDPBasePermission, ReadAndCreate)

from djangoldp_tems.models.__base_model import baseTEMSModel

logger = logging.getLogger(__name__)


def get_default_email_sender_djangoldp_instance():
    """
    :return: the configured email host if it can find one, or None
    """
    email_from = getattr(settings, "DEFAULT_FROM_EMAIL", False) or getattr(
        settings, "EMAIL_HOST_USER", False
    )
    if not email_from:
        jabber_host = getattr(settings, "JABBER_DEFAULT_HOST", False)

        if jabber_host:
            return "noreply@" + str(jabber_host)
        return None

    return email_from


class ReadCreateAndChange(LDPBasePermission):
    permissions = {"view", "add", "change"}


class RegisterParticipant(baseTEMSModel):
    status = models.CharField(
        max_length=32,
        default="pending",
        choices=(
            ("pending", "Pending"),
            ("approved", "Approve"),
            ("rejected", "Reject"),
        ),
        verbose_name="Validation Status",
    )
    firstname = models.CharField(max_length=255, verbose_name="first name")
    lastname = models.CharField(max_length=255, verbose_name="last name")
    email = models.EmailField(verbose_name="email")
    password = models.CharField(
        max_length=255, verbose_name="password", null=True, blank=True
    )
    organisation = models.CharField(max_length=255, verbose_name="organisation name")
    organisationAddress = models.CharField(
        max_length=255, verbose_name="organisation Address", null=True, blank=True
    )
    organisationRegistrationNumber = models.CharField(
        max_length=255,
        verbose_name="organisation Registration Number",
        null=True,
        blank=True,
    )
    optin_register = models.BooleanField(
        verbose_name="Accepts Terms and Conditions",
        default=False,
    )

    class Meta(baseTEMSModel.Meta):
        serializer_fields = baseTEMSModel.Meta.serializer_fields + [
            "status",
            "firstname",
            "lastname",
            "email",
            "organisation",
            "organisationAddress",
            "organisationRegistrationNumber",
            "optin_register",
        ]
        verbose_name = "RegisterParticipant"
        verbose_name_plural = "RegisterParticipants"
        rdf_type = ["tems:RegisterParticipant"]
        permission_classes = [(AuthenticatedOnly & ReadAndCreate) | CreateOnly]

    def __str__(self):
        return self.organisation

    def save(self, *args, **kwargs):
        if self._state.adding and not self.optin_register:
            raise ValidationError("You must accept the Terms and Conditions.")

        #TODO: Refactor, really hacky and strongly tied to the onboarding URL structure of the current VM
        if not self._state.adding and "/onboarding/" not in self.urlid:
            split_urlid = self.urlid.split("/registerparticipants/")
            self.urlid = split_urlid[0] + "/onboarding/registerparticipants/" + split_urlid[1]

        super().save(*args, **kwargs)


@receiver(pre_save, sender=RegisterParticipant)
def register_in_keycloak(sender, instance, **kwargs):
    """
    When a participant goes from any other status → 'approved',
    call Keycloak to create a matching user.
    """
    # only on updates
    if not instance.pk:
        return

    # fetch the “old” instance from the DB
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    # only fire when we go from pending → approved
    if old.status != "pending" or instance.status != "approved":
        return

    # 1) get token
    token_url = f"{settings.KEYCLOAK_BASE_URL}/auth/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token"
    token_payload = {
        "client_id": settings.KEYCLOAK_CLIENT_ID,
        "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
        "grant_type": "client_credentials",
    }
    try:
        token_response = requests.post(token_url, data=token_payload, timeout=10)
        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]
    except Exception as e:
        logger.error("Failed to fetch Keycloak token: %s", e)
        return

    # 2) register user
    user_url = f"{settings.KEYCLOAK_BASE_URL}/auth/admin/realms/{settings.KEYCLOAK_REALM}/users"
    username = f"{slugify(instance.firstname)}.{slugify(instance.lastname)}"
    user_payload = {
        "username": username,
        "firstName": instance.firstname,
        "lastName": instance.lastname,
        "enabled": True,
        "email": instance.email,
        "emailVerified": True,
        "credentials": [
            {"type": "password", "value": instance.password, "temporary": False}
        ],
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    try:
        user_creation = requests.post(user_url, json=user_payload, headers=headers, timeout=10)
        user_creation.raise_for_status()
        logger.info(
            "Created Keycloak user %s for participant %s", username, instance.pk
        )
    except Exception as e:
        logger.error("Failed to create Keycloak user %s: %s", username, e)


@receiver(post_save, sender=RegisterParticipant)
def send_organisation_confirmation_email(sender, instance, created, **kwargs):
    from_mail = get_default_email_sender_djangoldp_instance()
    if created:
        # Notify the admins of the new request
        admin_list = getattr(settings, "TEMS_ADMIN_MAILS", [])
        if admin_list and isinstance(admin_list, (list, tuple)):
            email_subject = "A new organisation is pending approval"

            html_template = get_template("email/notify_admin_creation.html")

            d = {
                "emailSender": {
                    "base_url": settings.BASE_URL,
                    "organisation_name": instance.organisation,
                }
            }

            html_content = html_template.render(d["emailSender"])
            html_without_css = re.sub(
                r"<style[^>]*>.*?</style>", "", html_content, flags=re.DOTALL
            )
            text_content = strip_tags(html_without_css)

            for admin in admin_list:
                email = EmailMultiAlternatives(
                    subject=email_subject,
                    body=text_content,
                    from_email=from_mail,
                    to=[admin],
                )
                email.attach_alternative(html_content, "text/html")
                email.send()

    if not created:
        # Notify the requester
        if instance.status == "rejected" or instance.status == "approved":
            if instance.status == "approved":
                email_subject = f"Your application to TEMS with the organization {instance.organisation} has been approved"
                html_template = get_template("email/notify_requester_approve.html")
            else:
                email_subject = (
                    f"Your organisation {instance.organisation} was {instance.status}"
                )
                html_template = get_template("email/notify_requester_rejected.html")

            d = {
                "emailSender": {
                    "base_url": settings.BASE_URL,
                    "fullname": f"{instance.firstname} {instance.lastname}",
                    "email": f"{instance.email}",
                }
            }

            html_content = html_template.render(d["emailSender"])
            html_without_css = re.sub(
                r"<style[^>]*>.*?</style>", "", html_content, flags=re.DOTALL
            )
            text_content = strip_tags(html_without_css)

            email = EmailMultiAlternatives(
                subject=email_subject,
                body=text_content,
                from_email=from_mail,
                to=[instance.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
