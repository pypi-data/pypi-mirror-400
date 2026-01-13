from django.db import models
from django.utils.translation import gettext_lazy as _

from djangoldp_tems.models.__base_named_model import baseTEMSNamedModel


class FeatureFlag(baseTEMSNamedModel):
    status = models.BooleanField(default=True)

    class Meta(baseTEMSNamedModel.Meta):
        verbose_name = _("Feature Flag")
        verbose_name_plural = _("Feature Flags")
        rdf_type = "tems:FeatureFlag"

        serializer_fields = baseTEMSNamedModel.Meta.serializer_fields + ["status"]
