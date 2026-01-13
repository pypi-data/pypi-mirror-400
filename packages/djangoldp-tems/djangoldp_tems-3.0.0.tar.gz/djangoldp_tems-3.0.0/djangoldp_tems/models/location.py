from django.db import models
from django.utils.translation import gettext_lazy as _

from djangoldp_tems.models.__base_named_model import baseTEMSNamedModel


class TEMSLocation(baseTEMSNamedModel):
    address = models.CharField(max_length=254, blank=True, null=True, default="")
    city = models.CharField(max_length=100, blank=True, null=True, default="")
    state = models.CharField(max_length=100, blank=True, null=True, default="")
    country = models.CharField(max_length=100, blank=True, null=True, default="")
    latitude = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=7, default=0)
    longitude = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=7, default=0)
    elevation = models.IntegerField(blank=True, null=True, default=0, help_text=_("Elevation in meters"))

    class Meta(baseTEMSNamedModel.Meta):
        container_path = "/objects/locations/"
        verbose_name = _("TEMS Location")
        verbose_name_plural = _("TEMS Locations")
        serializer_fields = baseTEMSNamedModel.Meta.serializer_fields + [
            "address",
            "city",
            "state",
            "country",
            "latitude",
            "longitude",
            "elevation",
        ]
        rdf_type = "tems:Location"
