from django.db import models
from django.utils.translation import gettext_lazy as _

from djangoldp_tems.models.__base_named_model import baseTEMSNamedModel


class TEMSLicence(baseTEMSNamedModel):
    short_desc = models.CharField(max_length=255, blank=True, null=True, default="")
    description = models.TextField(blank=True, null=True, default="")
    url = models.CharField(max_length=2000, blank=True, null=True, default="")

    def __str__(self):
        return self.name or self.url or self.urlid

    class Meta(baseTEMSNamedModel.Meta):
        container_path = "/objects/licences/"
        verbose_name = _("TEMS Licence")
        verbose_name_plural = _("TEMS Licences")

        serializer_fields = baseTEMSNamedModel.Meta.serializer_fields + [
            "short_desc",
            "description",
            "url",
        ]
        rdf_type = "tems:Licence"
