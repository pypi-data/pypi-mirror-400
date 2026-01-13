from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _

from djangoldp_object3d.models.category import Object3DCategory
from djangoldp_object3d.models.format import Object3DFormat
from djangoldp_object3d.models.keyword import Object3DKeyword
from djangoldp_tems.models.__base_object import baseTEMSObject
from djangoldp_tems.models.location import TEMSLocation
from djangoldp_tems.models.provider import TEMSProvider, register_catalog
from djangoldp_edc import EdcContractPermissionV3WithFallback, EdcContractPermissionV3


class Object3DObject(baseTEMSObject):
    providers = models.ManyToManyField(
        TEMSProvider, blank=True, related_name="catalog_object3d"
    )
    owners = models.OneToOneField(
        Group,
        related_name="owned_object3d",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    keywords = models.ManyToManyField(Object3DKeyword, blank=True)
    categories = models.ManyToManyField(Object3DCategory, blank=True)
    time_period = models.TextField(blank=True, null=True, default="")
    country = models.CharField(max_length=255, blank=True, null=True, default="")
    location = models.ForeignKey(
        TEMSLocation, blank=True, null=True, on_delete=models.SET_NULL
    )
    actual_representation = models.TextField(blank=True, null=True, default="")
    format = models.ForeignKey(
        Object3DFormat, blank=True, null=True, on_delete=models.SET_NULL
    )
    file_size = models.CharField(max_length=255, blank=True, null=True, default="")
    year = models.IntegerField(blank=True, null=True, default=0)
    texture = models.TextField(blank=True, null=True, default="")
    texture_formats = models.TextField(blank=True, null=True, default="")
    texture_resolution = models.TextField(blank=True, null=True, default="")
    polygons = models.IntegerField(blank=True, null=True, default=0)
    ai = models.BooleanField(default=False)
    allow_ai = models.BooleanField(default=False)
    prices = models.TextField(blank=True, null=True, default="")
    rights_holder = models.TextField(blank=True, null=True, default="")
    creator = models.TextField(blank=True, null=True, default="")

    class Meta(baseTEMSObject.Meta):
        container_path = "/objects/object3d/"
        verbose_name = _("TEMS 3D Object")
        verbose_name_plural = _("TEMS 3D Objects")
        permission_classes = [EdcContractPermissionV3, EdcContractPermissionV3WithFallback]

        serializer_fields = [
            "@id",
            "creation_date",
            "update_date",
            "title",
            "description",
            "copyright",
            "website",
            "licences",
            "images",
            "keywords",
            "categories",
            "time_period",
            "country",
            "location",
            "actual_representation",
            "format",
            "file_size",
            "year",
            "texture",
            "texture_formats",
            "texture_resolution",
            "polygons",
            "ai",
            "allow_ai",
            "prices",
            "rights_holder",
            "creator",
            "providers",
            "owners",
        ]
        nested_fields = [
            "licences",
            "images",
            "format",
            "categories",
            "location",
            "keywords",
            "providers",
        ]
        rdf_type = ["tems:Object", "tems:3DObject"]


register_catalog("object3d", Object3DObject)
