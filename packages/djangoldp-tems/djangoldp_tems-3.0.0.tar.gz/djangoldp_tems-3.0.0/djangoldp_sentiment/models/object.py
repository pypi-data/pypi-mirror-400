from django.db import models
from django.utils.translation import gettext_lazy as _

from djangoldp_sentiment.models.topic import SentimentTopic
from djangoldp_tems.models.__base_model import baseTEMSModel
from djangoldp_tems.models.location import TEMSLocation
from djangoldp_tems.models.provider import TEMSProvider, register_catalog


class Sentiment(baseTEMSModel):
    providers = models.ManyToManyField(
        TEMSProvider, blank=True, related_name="catalog_sentiment"
    )
    keyword = models.CharField(max_length=255, blank=True, null=True, default="")
    location = models.ForeignKey(
        TEMSLocation, blank=True, null=True, on_delete=models.SET_NULL
    )
    iframe = models.CharField(max_length=2000, blank=True, null=True, default="")
    topics = models.ManyToManyField(SentimentTopic, blank=True)

    def __str__(self):
        return self.keyword

    class Meta(baseTEMSModel.Meta):
        container_path = "/sentiments/"
        verbose_name = _("TEMS Sentiment")
        verbose_name_plural = _("TEMS Sentiments")

        serializer_fields = [
            "@id",
            "creation_date",
            "update_date",
            "keyword",
            "location",
            "iframe",
            "topics",
            "providers",
        ]
        nested_fields = [
            "location",
            "topics",
            "providers",
        ]
        rdf_type = ["tems:Sentiment"]


register_catalog("sentiment", Sentiment, False)
