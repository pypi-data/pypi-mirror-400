from django.contrib import admin
from django.utils.html import format_html

from djangoldp_onboarding.models import *
from djangoldp_tems.admin import TemsModelAdmin


@admin.register(RegisterParticipant)
class ParticipantAdmin(TemsModelAdmin):
    exclude = TemsModelAdmin.exclude + ("password",)
    readonly_fields = TemsModelAdmin.readonly_fields + ("password_masked",)

    fields = (
        "email",
        "firstname",
        "lastname",
        "password_masked",
        "organisation",
        "organisationAddress",
        "organisationRegistrationNumber",
        "optin_register",
        "status",
        "urlid",
    )

    def password_masked(self, obj):
        """
        Display the stored clear-text password in a disabled <input type="password">,
        so it's always hidden. If there's no object yet, show nothing.
        """
        if not obj or not obj.password:
            return ""
        # render_value=True is implicit here because we’re writing raw HTML
        return format_html(
            '<input type="password" value="{}" readonly disabled style="border:none;background:transparent;" />',
            obj.password,
        )

    password_masked.short_description = "Password"

    def save_model(self, request, obj, form, change):
        """
        If we're editing an existing instance, re-fetch the old password
        so that even if someone tampers with the form POST they can't change it.
        """
        if change:
            orig = RegisterParticipant.objects.get(pk=obj.pk)
            obj.password = orig.password
        super().save_model(request, obj, form, change)
