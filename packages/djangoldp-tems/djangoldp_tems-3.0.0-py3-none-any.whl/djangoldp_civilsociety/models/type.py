from django.utils.translation import gettext_lazy as _

from djangoldp_tems.models.__base_named_model import baseTEMSNamedModel


class CivilSocietyType(baseTEMSNamedModel):
    class Meta(baseTEMSNamedModel.Meta):
        container_path = "/objects/types/mediaobjects/civilsocieties/"
        verbose_name = _("TEMS Type")
        verbose_name_plural = _("TEMS Types")
        rdf_type = "tems:Type"
