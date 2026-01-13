from django.utils.translation import gettext_lazy as _

from djangoldp_tems.models.__base_named_model import baseTEMSNamedModel


class TEMSCategory(baseTEMSNamedModel):
    class Meta(baseTEMSNamedModel.Meta):
        abstract = True
        container_path = "/categories/"
        verbose_name = _("TEMS Category")
        verbose_name_plural = _("TEMS Categories")
        rdf_type = "tems:Category"
