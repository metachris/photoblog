import datetime
import logging
from django.db.models.signals import pre_save

from django.db import models
from django.contrib.auth.models import User
from django.dispatch.dispatcher import receiver
from treebeard.mp_tree import MP_Node

import caching.base
import tools


class UserProfile(caching.base.CachingMixin, models.Model):
    objects = caching.base.CachingManager()

    user = models.OneToOneField(User)
    date_created = models.DateTimeField('date created', auto_now_add=True)

    # Other fields here
    accepted_eula = models.BooleanField()

    def __unicode__(self):
        return "<UserProfile(%s)>" % self.user


class Tag(MP_Node):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=256, null=True)

    node_order_by = ['name']

    def __unicode__(self):
        return 'Tag: %s %s' % ("-" * (self.get_depth()-1), self.name)


class Set(caching.base.CachingMixin, models.Model):
    objects = caching.base.CachingManager()

    user = models.ForeignKey(User)
    date_created = models.DateTimeField('date created', auto_now_add=True)

    title = models.CharField(max_length=512)
    slug = models.CharField(max_length=512, null=True)

    cover_photo = models.ForeignKey("Photo", blank=True, null=True, related_name="set_cover")

    def __unicode__(self):
        return 'Set: %s' % self.title


class Photo(caching.base.CachingMixin, models.Model):
    """
    Ideas: exif info, related photos
    """
    objects = caching.base.CachingManager()

    user = models.ForeignKey(User)
    date_created = models.DateTimeField('date created', auto_now_add=True)

    #
    filename = models.CharField(max_length=512, blank=True)
    external_url = models.CharField(max_length=2048, blank=True)  # for photos on flickr, 500px, etc

    # Custom id
    hash = models.CharField(max_length=32)
    set = models.ForeignKey(Set, blank=True, null=True)

    # Image info
    tags = models.ManyToManyField(Tag, blank=True, null=True)
    views = models.IntegerField(default=0)

    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)

    description_md = models.CharField(max_length=10240, blank=True)  # markdown
    description_html = models.CharField(max_length=10240, blank=True)  # converted to html

    date_captured = models.DateTimeField('captured', blank=True, null=True)  # from exif

    @staticmethod
    def _mk_hash():
        hash = "daee3a"
        while not hash or Photo.objects.filter(hash=hash).count():
            hash = tools.id_generator(size=6, chars="abcdef0123456789")
        return hash

    @staticmethod
    def _mk_slug(title):
        slug = slug_orig = tools.slugify(title)
        count = 1
        while not slug or Photo.objects.filter(slug=slug).count():
            count += 1
            slug = slug_orig + str(count)
        return slug

    def __unicode__(self):
        return "<Photo(%s, %s)>" % (self.pk, self.title)


@receiver(pre_save, sender=Photo)
def photo_save_handler(sender, **kwargs):
    photo = kwargs["instance"]
    photo.slug = Photo._mk_slug(photo.title)
    print "new slug: %s" % photo.slug
    if not photo.hash:
        photo.hash = Photo._mk_hash()
        print "new hash: %s" % photo.hash
