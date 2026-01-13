from django.contrib import admin

from djangoldp_factchecking.models import *
from djangoldp_tems.admin import TemsModelAdmin

admin.site.register(FactCheckingAffiliation, TemsModelAdmin)
admin.site.register(FactCheckingObject, TemsModelAdmin)
admin.site.register(FactCheckingTopic, TemsModelAdmin)
