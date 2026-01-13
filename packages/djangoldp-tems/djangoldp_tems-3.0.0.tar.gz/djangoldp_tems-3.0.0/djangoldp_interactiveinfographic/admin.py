from django.contrib import admin

from djangoldp_interactiveinfographic.models import *
from djangoldp_tems.admin import TemsModelAdmin

admin.site.register(InteractiveInfographicObject, TemsModelAdmin)
