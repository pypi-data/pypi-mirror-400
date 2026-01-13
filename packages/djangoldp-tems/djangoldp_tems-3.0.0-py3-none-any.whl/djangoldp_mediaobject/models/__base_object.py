from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _

from djangoldp_mediaobject.models.asset import MediaObjectAsset
from djangoldp_mediaobject.models.keyword import MediaObjectKeyword
from djangoldp_mediaobject.models.language import MediaObjectLanguage
from djangoldp_tems.models.__base_object import baseTEMSObject
from djangoldp_tems.models.provider import TEMSProvider
from djangoldp_edc import EdcContractPermissionV3


class MediaObjectObject(baseTEMSObject):
    providers = models.ManyToManyField(
        TEMSProvider, blank=True, related_name="catalog_mediaobject"
    )
    owners = models.OneToOneField(
        Group,
        related_name="owned_mediaobject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    assets = models.ManyToManyField(MediaObjectAsset, blank=True)
    keywords = models.ManyToManyField(MediaObjectKeyword, blank=True)
    publication_date = models.DateTimeField(null=True)
    language = models.ForeignKey(
        MediaObjectLanguage, blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta(baseTEMSObject.Meta):
        abstract = True
        container_path = "/objects/mediaobjects/"
        verbose_name = _("TEMS Media Object")
        verbose_name_plural = _("TEMS Media Objects")
        permission_classes = [EdcContractPermissionV3]

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
        rdf_type = ["tems:Object", "tems:MediaObject"]
