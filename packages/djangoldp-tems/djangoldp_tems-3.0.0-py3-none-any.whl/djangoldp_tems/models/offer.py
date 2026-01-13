from django.db import models
from django.utils.translation import gettext_lazy as _

from djangoldp_tems.models.__base_named_model import baseTEMSNamedModel

KIND_OPTIONS = (
    ("subscription", _("Subscription")),
    ("purchase", _("Purchase")),
)

class TEMSOffer(baseTEMSNamedModel):
    kind = models.CharField(max_length=20, choices=KIND_OPTIONS, default="subscription")
    description = models.TextField(blank=True, null=True, default="")

    class Meta(baseTEMSNamedModel.Meta):
        container_path = "/offers/"
        verbose_name = _("TEMS Offer")
        verbose_name_plural = _("TEMS Offers")
        rdf_type = "tems:Offer"

        serializer_fields = baseTEMSNamedModel.Meta.serializer_fields + [
            "description",
            "kind",
        ]
