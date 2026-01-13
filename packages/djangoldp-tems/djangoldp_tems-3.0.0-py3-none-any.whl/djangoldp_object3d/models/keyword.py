from django.utils.translation import gettext_lazy as _

from djangoldp_tems.models.__base_named_model import baseTEMSNamedModel


class Object3DKeyword(baseTEMSNamedModel):
    class Meta(baseTEMSNamedModel.Meta):
        container_path = "/objects/keywords/3dobjects/"
        verbose_name = _("TEMS Keyword")
        verbose_name_plural = _("TEMS Keywords")
        rdf_type = "tems:Keyword"
