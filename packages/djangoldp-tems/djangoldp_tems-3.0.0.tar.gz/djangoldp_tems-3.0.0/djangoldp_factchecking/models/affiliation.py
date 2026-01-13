from django.utils.translation import gettext_lazy as _

from djangoldp_tems.models.format import TEMSFormat


class FactCheckingAffiliation(TEMSFormat):
    class Meta(TEMSFormat.Meta):
        container_path = "/objects/affiliations/mediaobjects/factcheckings/"
        verbose_name = _("TEMS Affiliation")
        verbose_name_plural = _("TEMS Affiliations")
        rdf_type = "tems:Affiliation"
