from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _

from djangoldp_factchecking.models.affiliation import FactCheckingAffiliation
from djangoldp_factchecking.models.topic import FactCheckingTopic
from djangoldp_mediaobject.models.__base_object import MediaObjectObject
from djangoldp_tems.models.location import TEMSLocation
from djangoldp_tems.models.provider import TEMSProvider, register_catalog
from djangoldp_edc import EdcContractPermissionV3WithFallback


class FactCheckingObject(MediaObjectObject):
    providers = models.ManyToManyField(
        TEMSProvider, blank=True, related_name="catalog_factchecking"
    )
    owners = models.OneToOneField(
        Group,
        related_name="owned_factchecking",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    location = models.ForeignKey(
        TEMSLocation,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    organisation = models.CharField(max_length=255, blank=True, null=True, default="")
    person = models.CharField(max_length=255, blank=True, null=True, default="")
    version = models.CharField(max_length=255, blank=True, null=True, default="")
    affiliation = models.ForeignKey(
        FactCheckingAffiliation,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    topics = models.ManyToManyField(FactCheckingTopic, blank=True)

    class Meta(MediaObjectObject.Meta):
        container_path = "/objects/mediaobjects/factcheckings/"
        verbose_name = _("TEMS Fact Checking")
        verbose_name_plural = _("TEMS Fact Checkings")

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
            "affiliation",
            "assets",
            "topics",
            "providers",
            "owners",
        ]
        nested_fields = [
            "licences",
            "assets",
            "images",
            "keywords",
            "language",
            "affiliation",
            "topics",
            "providers",
        ]
        rdf_type = ["tems:Object", "tems:MediaObject", "tems:FactChecking"]


register_catalog("factchecking", FactCheckingObject)
