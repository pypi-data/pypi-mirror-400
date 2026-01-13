from django.contrib import admin

from djangoldp_civilsociety.models import *
from djangoldp_tems.admin import TemsModelAdmin

admin.site.register(CivilSocietyObject, TemsModelAdmin)
admin.site.register(CivilSocietyType, TemsModelAdmin)
