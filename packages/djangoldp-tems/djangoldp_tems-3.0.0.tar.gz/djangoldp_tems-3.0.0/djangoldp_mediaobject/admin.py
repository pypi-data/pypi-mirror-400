from django.contrib import admin

from djangoldp_mediaobject.models import *
from djangoldp_tems.admin import TemsModelAdmin

admin.site.register(MediaObjectLanguage, TemsModelAdmin)
