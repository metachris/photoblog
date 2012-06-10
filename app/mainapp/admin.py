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
    list_display = ["id", "title", "order_id", "published", "slug", "hash", "fn_ext", "url"]
    list_filter = ("published",)

    fieldsets = (
        (None, {
            "fields": ("hash", "fn_ext", "revisions", "revision_set", "url", "order_id")

        }),
        ("Image Information", {
            "fields": ("user", "photographer", "title", "slug", "description_md", "sets", "tags", "location", "published", "featured")
        }),

        ("Image Meta Information", {
            "fields": ("date_captured", "filesize", "resolution_width", "resolution_height",
                       "upload_resolution_width", "upload_resolution_height", "upload_filename", "upload_filename_from",
                       "upload_filesize")
        }),
        ("Exif Information", {
            #'classes': ('collapse',),
            "fields": ("exif", "exif_camera", "exif_lens", "exif_exposuretime", "exif_aperture", "exif_iso", "exif_focallength", "exif_flash")
        }),
    )

    readonly_fields = ["revisions", "order_id", "url", "hash", "fn_ext", "filesize", "resolution_width", "resolution_height",
                       "upload_resolution_width", "upload_resolution_height", "upload_filename", "upload_filesize", "upload_filename_from"]
    exclude = ["description_html", "is_original"]


class AdminValueAdmin(admin.ModelAdmin):
    list_display = ["key", "val", "enabled", "id"]
    list_filter = ("enabled",)


class HandoutContactAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "tel"]


admin.site.register(models.UserProfile)
admin.site.register(models.Tag, MP_Tag_Admin)
admin.site.register(models.Photo, PhotoAdmin)
admin.site.register(models.Set)
admin.site.register(models.Location, MP_Location_Admin)

admin.site.register(models.Handout)
admin.site.register(models.HandoutContact, HandoutContactAdmin)
admin.site.register(models.AdminValue, AdminValueAdmin)
