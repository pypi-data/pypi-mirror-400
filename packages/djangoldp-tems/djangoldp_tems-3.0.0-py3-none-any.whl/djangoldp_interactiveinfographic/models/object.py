from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _

from djangoldp_mediaobject.models.__base_object import MediaObjectObject
from djangoldp_tems.models.provider import TEMSProvider, register_catalog


class InteractiveInfographicObject(MediaObjectObject):
    providers = models.ManyToManyField(
        TEMSProvider, blank=True, related_name="catalog_interactiveinfographic"
    )
    owners = models.OneToOneField(
        Group,
        related_name="owned_interactiveinfographic",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    instruction = models.TextField(blank=True, null=True, default="")

    class Meta(MediaObjectObject.Meta):
        container_path = "/objects/mediaobjects/interactiveinfographics/"
        verbose_name = _("TEMS Interactive Infographic")
        verbose_name_plural = _("TEMS Interactive Infographics")

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
            "publication_date",
            "language",
            "assets",
            "instruction",
            "providers",
            "owners",
        ]
        nested_fields = [
            "licences",
            "assets",
            "images",
            "keywords",
            "language",
            "providers",
        ]
        rdf_type = ["tems:Object", "tems:MediaObject", "tems:InteractiveInfographic"]


register_catalog("interactiveinfographic", InteractiveInfographicObject)
