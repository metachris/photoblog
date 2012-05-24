import models
from django.contrib import admin
import treebeard.admin

class MP_Tag_Admin(treebeard.admin.TreeAdmin):
    pass

admin.site.register(models.UserProfile)
admin.site.register(models.Tag, MP_Tag_Admin)
admin.site.register(models.Photo)
