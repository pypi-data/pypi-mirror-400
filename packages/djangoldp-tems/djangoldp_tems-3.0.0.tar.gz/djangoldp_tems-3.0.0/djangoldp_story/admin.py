from django.contrib import admin

from djangoldp_story.models import *
from djangoldp_tems.admin import TemsModelAdmin

admin.site.register(StoryObject, TemsModelAdmin)
admin.site.register(StoryType, TemsModelAdmin)
