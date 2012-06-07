import os
import datetime
import logging
from django.db.models.signals import pre_save, post_delete

from django.db import models
from django.contrib.auth.models import User
from django.dispatch.dispatcher import receiver
from django.template.defaultfilters import slugify
from django.conf import settings
from treebeard.mp_tree import MP_Node
import caching.base

import markdown

import tools


log = logging.getLogger(__name__)


class UserProfile(caching.base.CachingMixin, models.Model):
    objects = caching.base.CachingManager()

    user = models.OneToOneField(User, null=True, blank=True)

    date_created = models.DateTimeField('date created', auto_now_add=True)
    is_photographer = models.BooleanField(default=True)

    # Other fields here
    accepted_eula = models.BooleanField()

    # Contact info
    name = models.CharField(max_length=512, blank=False, null=True)
    email = models.EmailField(blank=True, null=True)
    tel = models.CharField(max_length=50, blank=True, null=True)

    @staticmethod
    def get_or_create(user):
        try:
            profile = UserProfile.objects.get(user=user)
        except Exception as e:
            print "create userprofile", e
            profile = UserProfile(user=user)
            profile.save()
        return profile

    def __unicode__(self):
        return "<UserProfile(%s, %s)>" % (self.user, self.name)


class AdminValue(caching.base.CachingMixin, models.Model):
    objects = caching.base.CachingManager()

    key = models.CharField(max_length=50)
    val = models.TextField()

    def __unicode__(self):
        return "<AdminValue(%s='%s')>" % (self.key, self.val)


class Tag(MP_Node):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=256, null=True, unique=True)

    node_order_by = ['name']

    def __unicode__(self):
        return 'Tag: %s %s' % ("-" * (self.get_depth()-1), self.name)


class Location(MP_Node):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=256, null=True, unique=True)

    node_order_by = ['name']

    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        return 'Location: %s %s' % ("-" * (self.get_depth()-1), self.name)


class Set(caching.base.CachingMixin, models.Model):
    objects = caching.base.CachingManager()

    user = models.ForeignKey(User)
    date_created = models.DateTimeField('date created', auto_now_add=True)
    published = models.BooleanField(default=False)

    title = models.CharField(max_length=512)
    slug = models.CharField(max_length=512, null=True, unique=True)

    description_md = models.TextField(blank=True, null=True)  # markdown
    description_html = models.TextField(blank=True, null=True)  # converted to html

    cover_photo = models.ForeignKey("Photo", blank=True, null=True, related_name="set_cover")

    def __unicode__(self):
        return 'Set: %s' % self.title


class Photo(caching.base.CachingMixin, models.Model):
    """
    """
    objects = caching.base.CachingManager()
    date_created = models.DateTimeField('date created', auto_now_add=True)
    order_id = models.IntegerField(default=0)

    # Who uploaded the photo
    user = models.ForeignKey(User)

    # Who captured this photo
    photographer = models.ForeignKey(UserProfile, blank=True, null=True)

    # If the uploaded image is an original
    is_original = models.BooleanField(default=False)

    # Use only one of either filename or an external url
    local_filename = models.CharField(max_length=512, blank=True, null=True)
    external_url = models.CharField(max_length=2048, blank=True)  # deprecated

    # URL to use for displaying the primary image. Auto-computed based on
    # whether the original is available, or an external url.
    # eg. <MEDIA_URL>/photo/123123.png or http://500px.com/...
    url = models.URLField()

    # Title, slug and hash
    title = models.CharField(max_length=100, blank=True, null=True)
    slug = models.CharField(max_length=100, blank=True, null=True, unique=True)  # can be auto-generated with Photo._mk_slug
    hash = models.CharField(max_length=32)

    # Image info
    description_md = models.TextField(blank=True, null=True)  # markdown
    description_html = models.TextField(blank=True, null=True)  # converted to html

    sets = models.ManyToManyField(Set, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, null=True)
    location = models.ForeignKey(Location, blank=True, null=True)

    date_captured = models.DateField('captured', blank=True, null=True)  # from exif

    # Whether this photo is publicly accessible
    published = models.BooleanField(default=False)

    # Whether this photo should be featured on the front page, etc.
    featured = models.BooleanField(default=False)

    # Photo Infos...
    filesize = models.IntegerField(null=True, blank=True)  # bytes

    # Resolution of the processed base image
    resolution_width = models.IntegerField(blank=True, null=True)   # px
    resolution_height = models.IntegerField(blank=True, null=True)  # px

    # Resolution of the uploaded image
    upload_resolution_width = models.IntegerField(blank=True, null=True)   # px
    upload_resolution_height = models.IntegerField(blank=True, null=True)  # px

    # Filename of the upload could have a different extension (keeps orig)
    upload_filename = models.CharField(max_length=512, blank=True, null=True)
    upload_filesize = models.IntegerField(null=True, blank=True)  # bytes

    # Filename pass along with the html form
    upload_filename_from = models.CharField(max_length=512, blank=True, null=True)

    # Exif info (currently stored on upload)
    exif = models.TextField(blank=True)  # JSON dump of exif dictionary

    # Selected exif tags
    exif_camera = models.CharField(max_length=512, blank=True, null=True)
    exif_lens = models.CharField(max_length=512, blank=True, null=True)

    exif_exposuretime = models.CharField(max_length=512, blank=True, null=True)
    exif_aperture = models.CharField(max_length=512, blank=True, null=True)
    exif_iso = models.CharField(max_length=512, blank=True, null=True)
    exif_focallength = models.CharField(max_length=512, blank=True, null=True)
    exif_flash = models.CharField(max_length=512, blank=True, null=True)

    @staticmethod
    def _mk_hash():
        hash = None
        while not hash or Photo.objects.filter(hash=hash).count():
            hash = tools.id_generator(size=6)
        return hash

    @staticmethod
    def _mk_slug(title):
        slug = slug_orig = slugify(title)
        if not slug:
            return
        count = 1
        while not slug or Photo.objects.filter(slug=slug).count():
            count += 1
            slug = slug_orig + str(count)
        return slug

    def __unicode__(self):
        return "<Photo(%s, %s)>" % (self.pk, self.title)

    def update_url(self):
        if self.local_filename:
            self.url = os.path.join(settings.MEDIA_URL, settings.MEDIA_DIR_PHOTOS, self.local_filename)
        elif self.external_url:
            self.url = self.external_url
        else:
            raise TypeError("Could not build an url for photo %s (local_filename=%s)" % (self, self.local_filename))

    @property
    def is_portrait(self):
        return self.resolution_height > self.resolution_width

    @staticmethod
    def post_delete_handler(sender, **kwargs):
        """Called when an image is deleted. Remove the image files."""
        photo = kwargs["instance"]
        log.info("Photo post delete handler: removing image files '%s'" % photo.local_filename)
        if photo.local_filename:
            fn_upload = os.path.join(settings.MEDIA_ROOT, settings.MEDIA_DIR_UPLOAD, photo.local_filename)
            fn_photo = os.path.join(settings.MEDIA_ROOT, settings.MEDIA_DIR_PHOTOS, photo.local_filename)
            os.remove(fn_upload)
            os.remove(fn_photo)
            log.info("- all removed")
        else:
            log.info("- no local filename")

    @staticmethod
    def pre_save_handler(sender, **kwargs):
        """Before saving update hash, slug, url and description_html"""
        photo = kwargs["instance"]
        if not photo.hash:
            photo.hash = Photo._mk_hash()
        if not photo.slug:
            photo.slug = Photo._mk_slug(photo.title)
        if photo.description_md:
            md = markdown.Markdown(safe_mode="escape")
            photo.description_html = md.convert(photo.description_md)
        photo.update_url()


# Registering Signals. using `connect()` prevents receiving signals twice (as happens with @receiver)
post_delete.connect(Photo.post_delete_handler, Photo, dispatch_uid="mainapp.models")
pre_save.connect(Photo.pre_save_handler, Photo, dispatch_uid="mainapp.models")


"""
    Models for hand-outs (id's handed to people, who can use it to get their photos
"""
class HandoutContact(models.Model):
    date_created = models.DateTimeField('date created', auto_now_add=True)
    hash = models.CharField(max_length=32)

    name = models.CharField(max_length=512, blank=False)

    email = models.EmailField(blank=True, null=True)
    tel = models.CharField(max_length=50, blank=True, null=True)

    subscribed_to_mail_list = models.BooleanField(default=False)

    @staticmethod
    def _mk_hash():
        hash = None
        while not hash or HandoutContact.objects.filter(hash=hash).count():
            hash = tools.id_generator(size=6)
        return hash

    def __unicode__(self):
        return "<Contact(%s, email=%s, tel=%s)>" % (self.name, self.email, self.tel)


class Handout(models.Model):
    """
    Reference for other people which have got an id and want to see their photos

    References a number of photos and sets
    """
    date_created = models.DateTimeField('date created', auto_now_add=True)
    contacts = models.ManyToManyField(HandoutContact, blank=True, null=True)
    views = models.IntegerField(default=0)
    hash = models.CharField(max_length=32)
    is_published = models.BooleanField(default=False)

    has_notified_contacts = models.BooleanField(default=False)
    date_notified_contacts = models.DateTimeField(blank=True, null=True)

    # Info for the viewer
    description_md = models.TextField(blank=True, null=True)  # markdown
    description_html = models.TextField(blank=True, null=True)  # converted to html

    # Data
    photos = models.ManyToManyField(Photo, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, null=True)

    @staticmethod
    def _mk_hash():
        hash = None
        while not hash or Handout.objects.filter(hash=hash).count():
            hash = tools.id_generator(size=6)
        return hash

    def __unicode__(self):
        return "<Handout(%s, %s)>" % (self.id, self.hash)


class HandoutMessage(models.Model):
    """
    Message thread for handout
    """
    date_created = models.DateTimeField('date created', auto_now_add=True)
    handout = models.ForeignKey(Handout)

    # Either from user of contact
    from_user = models.ForeignKey(User, blank=True, null=True)
    from_contact = models.ForeignKey(HandoutContact, blank=True, null=True)

    # Content
    description_md = models.TextField(blank=True, null=True)  # markdown
    description_html = models.TextField(blank=True, null=True)  # auto-converted to html

    def __unicode__(self):
        return "HandoutMessage: %s" % (self.id)
