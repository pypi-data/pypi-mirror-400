from django.utils.translation import gettext_lazy as _

from djangoldp_tems.models.__base_named_model import baseTEMSNamedModel


class MediaObjectKeyword(baseTEMSNamedModel):
    class Meta(baseTEMSNamedModel.Meta):
        container_path = "/objects/keywords/mediaobjects/"
        verbose_name = _("TEMS Keyword")
        verbose_name_plural = _("TEMS Keywords")
        rdf_type = "tems:Keyword"
