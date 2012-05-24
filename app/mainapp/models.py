import datetime

from django.db import models
from django.contrib.auth.models import User
from treebeard.mp_tree import MP_Node

import caching.base


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
    slug = models.CharField(max_length=256)

    node_order_by = ['name']

    def __unicode__(self):
        return 'Tag: %s' % self.name


class Set(caching.base.CachingMixin, models.Model):
    objects = caching.base.CachingManager()

    user = models.ForeignKey(User)
    date_created = models.DateTimeField('date created', auto_now_add=True)

    title = models.CharField(max_length=512)
    slug = models.CharField(max_length=512)


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

    def __unicode__(self):
        return "<Photo(%s)>" % self.pk
