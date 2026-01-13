from email.mime import base

from django.db import models
from django.utils.translation import gettext_lazy as _

from djangoldp_tems.models.__base_named_model import baseTEMSNamedModel
from djangoldp_tems.models.image import TEMSImage
from djangoldp_tems.models.licence import TEMSLicence
from djangoldp_tems.models.provider import TEMSProvider
from djangoldp_tems.models.provider_category import TEMSProviderCategory


class TEMSService(baseTEMSNamedModel):
    provider = models.ForeignKey(
        TEMSProvider,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="services",
    )
    description = models.TextField(blank=True, null=True, default="")
    long_description = models.TextField(blank=True, null=True, default="")
    categories = models.ManyToManyField(TEMSProviderCategory, blank=True)
    activation_status = models.BooleanField(default=False)
    activation_date = models.DateTimeField(blank=True, null=True)
    licence = models.ForeignKey(
        TEMSLicence,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    is_in_app = models.BooleanField(default=False)
    is_external = models.BooleanField(default=False)
    is_api = models.BooleanField(default=False)
    images = models.ManyToManyField(TEMSImage, blank=True)
    release_date = models.DateTimeField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)
    developper = models.ForeignKey(
        TEMSImage,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="service_developper",
    )
    contact_url = models.CharField(max_length=2000, blank=True, null=True, default="")
    documentation_url = models.CharField(
        max_length=2000, blank=True, null=True, default=""
    )

    class Meta(baseTEMSNamedModel.Meta):
        container_path = "/services/"
        verbose_name = _("TEMS Service")
        verbose_name_plural = _("TEMS Services")

        serializer_fields = baseTEMSNamedModel.Meta.serializer_fields + [
            "description",
            "long_description",
            "categories",
            "activation_status",
            "activation_date",
            "licence",
            "is_in_app",
            "is_external",
            "is_api",
            "images",
            "release_date",
            "last_update",
            "developper",
            "contact_url",
            "documentation_url",
            "provider",
            "data_offers",
        ]
        nested_fields = [
            "categories",
            "licence",
            "images",
            "developper",
        ]
        rdf_type = "tems:Service"
