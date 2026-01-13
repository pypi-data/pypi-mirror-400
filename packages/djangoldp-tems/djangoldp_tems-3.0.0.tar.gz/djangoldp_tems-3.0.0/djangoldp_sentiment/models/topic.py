from django.utils.translation import gettext_lazy as _

from djangoldp_tems.models.__base_named_model import baseTEMSNamedModel


class SentimentTopic(baseTEMSNamedModel):
    class Meta(baseTEMSNamedModel.Meta):
        container_path = "/objects/topics/sentiments/"
        verbose_name = _("TEMS Topic")
        verbose_name_plural = _("TEMS Topics")
        rdf_type = "tems:Topic"
