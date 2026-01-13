from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _

from djangoldp_civilsociety.models.type import CivilSocietyType
from djangoldp_mediaobject.models.__base_object import MediaObjectObject
from djangoldp_tems.models.provider import TEMSProvider, register_catalog


class CivilSocietyObject(MediaObjectObject):
    providers = models.ManyToManyField(
        TEMSProvider, blank=True, related_name="catalog_civilsociety"
    )
    owners = models.OneToOneField(
        Group,
        related_name="owned_civilsociety",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    editor = models.CharField(max_length=255, blank=True, null=True, default="")
    original_languages = models.CharField(max_length=255, blank=True, null=True, default="")
    contributors = models.CharField(max_length=255, blank=True, null=True, default="")
    publication_service = models.CharField(max_length=255, blank=True, null=True, default="")
    type = models.ForeignKey(
        CivilSocietyType,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta(MediaObjectObject.Meta):
        container_path = "/objects/mediaobjects/civilsocieties/"
        verbose_name = _("TEMS Civil Society")
        verbose_name_plural = _("TEMS Civil Societies")

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
            "editor",
            "original_languages",
            "contributors",
            "publication_service",
            "type",
            "providers",
            "owners",
        ]
        nested_fields = [
            "licences",
            "assets",
            "images",
            "keywords",
            "language",
            "type",
            "providers",
        ]
        rdf_type = ["tems:Object", "tems:MediaObject", "tems:CivilSociety"]


register_catalog("civilsociety", CivilSocietyObject)
