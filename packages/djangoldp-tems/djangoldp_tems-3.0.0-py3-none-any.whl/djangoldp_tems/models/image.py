from django.db import models
from django.utils.translation import gettext_lazy as _

from djangoldp_tems.models.__base_named_model import baseTEMSNamedModel


class TEMSImage(baseTEMSNamedModel):
    url = models.CharField(max_length=2000, blank=True, null=True, default="")
    iframe = models.BooleanField(default=False)

    def __str__(self):
        return self.name or self.url or self.urlid

    class Meta(baseTEMSNamedModel.Meta):
        container_path = "/objects/images/"
        verbose_name = _("TEMS Image")
        verbose_name_plural = _("TEMS Images")

        serializer_fields = baseTEMSNamedModel.Meta.serializer_fields + [
            "url",
            "iframe",
        ]
        rdf_type = "tems:Image"
