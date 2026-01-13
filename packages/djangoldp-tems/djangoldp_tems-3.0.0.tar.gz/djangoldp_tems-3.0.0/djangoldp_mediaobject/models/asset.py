from django.db import models
from django.utils.translation import gettext_lazy as _

from djangoldp_mediaobject.models.category import MediaObjectCategory
from djangoldp_mediaobject.models.format import MediaObjectFormat
from djangoldp_tems.models.__base_named_model import baseTEMSNamedModel


class MediaObjectAsset(baseTEMSNamedModel):
    size = models.PositiveBigIntegerField(blank=True, null=True, default=0)
    format = models.ForeignKey(
        MediaObjectFormat, blank=True, null=True, on_delete=models.SET_NULL
    )
    categories = models.ManyToManyField(MediaObjectCategory, blank=True)

    class Meta(baseTEMSNamedModel.Meta):
        container_path = "/objects/assets/mediaobjects/"
        verbose_name = _("TEMS Asset")
        verbose_name_plural = _("TEMS Assets")

        serializer_fields = baseTEMSNamedModel.Meta.serializer_fields + [
            "size",
            "format",
            "categories",
        ]
        nested_fields = [
            "format",
            "categories",
        ]
        rdf_type = "tems:Asset"
