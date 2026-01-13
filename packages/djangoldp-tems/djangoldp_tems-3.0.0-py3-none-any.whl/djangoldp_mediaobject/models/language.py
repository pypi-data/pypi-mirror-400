from django.utils.translation import gettext_lazy as _

from djangoldp_tems.models.__base_named_model import baseTEMSNamedModel


class MediaObjectLanguage(baseTEMSNamedModel):
    class Meta(baseTEMSNamedModel.Meta):
        container_path = "/objects/languages/mediaobjects/"
        verbose_name = _("TEMS Language")
        verbose_name_plural = _("TEMS Languages")

        rdf_type = "tems:Language"
