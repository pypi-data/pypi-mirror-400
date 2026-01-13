from django.db import models
from django.utils.translation import gettext_lazy as _

from djangoldp_tems.models.__base_model import baseTEMSModel


class baseTEMSNamedModel(baseTEMSModel):
    name = models.CharField(max_length=254, blank=True, null=True, default="")

    def __str__(self):
        return self.name or self.urlid

    class Meta(baseTEMSModel.Meta):
        abstract = True
        serializer_fields = [
            "@id",
            "creation_date",
            "update_date",
            "name",
        ]
