import models
from django.contrib import admin
import treebeard.admin

class MP_Tag_Admin(treebeard.admin.TreeAdmin):
    pass

class PhotoAdmin(admin.ModelAdmin):
    list_display = ["title", "id", "slug", "hash"]
    exclude = ["hash", "slug", "description_html", "views"]


admin.site.register(models.UserProfile)
admin.site.register(models.Tag, MP_Tag_Admin)
admin.site.register(models.Photo, PhotoAdmin)
admin.site.register(models.Set)
