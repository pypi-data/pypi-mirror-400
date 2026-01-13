from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.models import Model
from djangoldp.permissions import AuthenticatedOnly, ReadOnly


class baseTEMSModel(Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.urlid

    class Meta(Model.Meta):
        abstract = True
        verbose_name = _("TEMS Unknown Object")
        verbose_name_plural = _("TEMS Unknown Objects")

        serializer_fields = [
            "@id",
            "creation_date",
            "update_date",
        ]
        nested_fields = []
        rdf_type = "tems:BasicObject"
        permission_classes = [AuthenticatedOnly & ReadOnly]
