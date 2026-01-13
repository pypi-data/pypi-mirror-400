from django.contrib import admin

from djangoldp_sentiment.models import *
from djangoldp_tems.admin import TemsModelAdmin

admin.site.register(SentimentTopic, TemsModelAdmin)
admin.site.register(Sentiment, TemsModelAdmin)
