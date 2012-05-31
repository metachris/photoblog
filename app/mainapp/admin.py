import models
from django.contrib import admin
from django import forms
import treebeard.admin

class MP_Tag_Admin(treebeard.admin.TreeAdmin):
    pass


class MP_Location_Admin(treebeard.admin.TreeAdmin):
    pass


class PhotoModelForm( forms.ModelForm ):
    descr = forms.CharField( widget=forms.Textarea )
    class Meta:
        model = models.Photo


class PhotoAdmin(admin.ModelAdmin):
    list_display = ["title", "id", "slug", "url"]
    exclude = ["slug", "description_html", "external_url", "url"]


admin.site.register(models.UserProfile)
admin.site.register(models.Tag, MP_Tag_Admin)
admin.site.register(models.Photo, PhotoAdmin)
admin.site.register(models.Set)
admin.site.register(models.Location, MP_Location_Admin)

admin.site.register(models.Handout)
admin.site.register(models.HandoutContact)
