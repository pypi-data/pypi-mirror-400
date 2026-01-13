from django.utils.translation import gettext_lazy as _

from djangoldp_tems.models.__base_named_model import baseTEMSNamedModel


class TEMSFormat(baseTEMSNamedModel):
    class Meta(baseTEMSNamedModel.Meta):
        abstract = True
        container_path = "/formats/"
        verbose_name = _("TEMS Format")
        verbose_name_plural = _("TEMS Formats")
        rdf_type = "tems:Format"
