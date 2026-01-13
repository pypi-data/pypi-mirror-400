from django.contrib import admin
from django.contrib.auth.models import Group
from djangoldp.admin import DjangoLDPAdmin

from djangoldp_tems.forms import GroupAdminForm
from djangoldp_tems.models import *


class EmptyAdmin(admin.ModelAdmin):
    readonly_fields = (
        "urlid",
        "creation_date",
        "update_date",
    )
    exclude = ("is_backlink", "allow_create_backlink")

    def get_model_perms(self, request):
        return {}


@admin.register(
    FeatureFlag,
    TEMSImage,
    TEMSLicence,
    TEMSProvider,
    TEMSProviderCategory,
    TEMSLocation,
    TEMSOffer,
    TEMSDataOffer,
    TEMSService,
)
class TemsModelAdmin(DjangoLDPAdmin):
    readonly_fields = (
        "urlid",
        "creation_date",
        "update_date",
    )
    exclude = ("is_backlink", "allow_create_backlink")
    extra = 0


admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    form = GroupAdminForm
    readonly_fields = ("name",)

    def get_model_perms(self, request):
        return {}
