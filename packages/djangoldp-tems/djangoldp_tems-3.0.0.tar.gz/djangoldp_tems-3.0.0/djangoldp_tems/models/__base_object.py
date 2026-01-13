from django.db import models
from django.utils.translation import gettext_lazy as _

from djangoldp_tems.models.__base_model import baseTEMSModel
from djangoldp_tems.models.image import TEMSImage
from djangoldp_tems.models.licence import TEMSLicence
from djangoldp_tems.models.provider import TEMSProvider


class baseTEMSObject(baseTEMSModel):
    title = models.CharField(max_length=254, blank=True, null=True, default="")
    description = models.TextField(blank=True, null=True, default="")
    copyright = models.CharField(max_length=254, blank=True, null=True, default="")
    website = models.CharField(max_length=2000, blank=True, null=True, default="")
    licences = models.ManyToManyField(TEMSLicence, blank=True)
    images = models.ManyToManyField(TEMSImage, blank=True)
    providers = models.ManyToManyField(TEMSProvider, blank=True)

    def __str__(self):
        return self.title or self.urlid

    class Meta(baseTEMSModel.Meta):
        abstract = True
        # TODO: Refine depth to avoid redundancy
        depth = 0
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
            "providers",
            "owners",
        ]
        nested_fields = [
            "licences",
            "images",
            "providers",
        ]
        rdf_type = "tems:Object"
