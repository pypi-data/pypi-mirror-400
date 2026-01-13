from django.contrib import admin

from djangoldp_object3d.models import *
from djangoldp_tems.admin import TemsModelAdmin

admin.site.register(Object3DCategory, TemsModelAdmin)
admin.site.register(Object3DFormat, TemsModelAdmin)
admin.site.register(Object3DKeyword, TemsModelAdmin)
admin.site.register(Object3DObject, TemsModelAdmin)
