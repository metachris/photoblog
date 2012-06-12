import hashlib
import logging

from django.core.cache import cache
from django.conf import settings

import mainapp.models as models
from mainapp import adminvalues

log = logging.getLogger(__name__)


class Filters(object):
    """
    Represent any possible combination of filters for browsing the photos.

    This class simplifies using this system by having the code in one place
    and referencing it from many views.
    """
    tags = None  # list of tag slugs
    sets = None  # list of set slugs
    location = None  # location slug
    featured_only = None

    # For paging
    last_hash = None

    def __init__(self, *args, **kwargs):
        """Lazy init method (eg. Filters(tags=[mytags]))"""
        for key in kwargs:
            if not hasattr(self, key):
                err = "Value '%s' is not available in Filters." % key
                log.error(err)
                raise AttributeError(err)
            setattr(self, key, kwargs[key])

    @staticmethod
    def from_dict(vars):
        return Filters(
            last_hash=vars.get("last_hash") or None,
            location=vars.get("location") or None,
            featured_only=True if vars.get("featured_only") == "1" else \
                    False if vars.get("featured_only") is "-1" else None,
            tags=vars.get("tags").split("+") if vars.get("tags") else None,
            sets=vars.get("sets").split("+") if vars.get("sets") else None
        )

    def to_dict(self):
        keys = ["tags", "sets", "location", "featured_only", "last_hash"]
        return { k: getattr(self, k) for k in keys }

    def to_html_dict(self):
        r = {
            "tags": "+".join(self.tags) if self.tags else "",
            "sets": "+".join(self.sets) if self.sets else "",
            "location": self.location or "",
            "featured_only": 1 if self.featured_only else -1 if self.featured_only is not None else 0,
            "last_hash": self.last_hash or "",
        }
        return r

    def __str__(self):
        return "<Filters%s>" % self.to_dict()


def filters_to_query(filters, limit=None):
    """
    This method builds a QuerySet out of one  filters object

    If limit is None, find all matching objects, else limit to supplied value
    """
    # 1. see if this query is already cached
    query = models.Photo.objects.filter(published=True)

    if filters.last_hash:
        photo_last = models.Photo.objects.get(hash=filters.last_hash)
        query = query.filter(order_id__lt=photo_last.order_id)

    if filters.featured_only:
        query = query.filter(featured=True)

    if filters.tags:
        # These tags and all their descendants
        tags = []
        for tag_slug in filters.tags:
            tag = models.Tag.objects.get(slug=tag_slug)
            tags += [tag]
            tags += tag.get_descendants()
        query = query.filter(tags__in=tags)

    if filters.sets:
        # These sets and all their descendants
        sets = []
        for set_slug in filters.sets:
            _set = models.Set.objects.get(slug=set_slug)
            sets += [_set]
        query = query.filter(sets__in=sets)

    if filters.location:
        locations = []
        l = models.Location.objects.get(slug=filters.location)
        locations += [l]
        locations += l.get_descendants()
        query = query.filter(location__in=locations)

    query = query.order_by("-order_id")
    if limit:
        query = query[:limit]

    return query


class ThumbnailPager(object):
    """
    Helper to move between pages
    """
    filters = None
    photos = None

    last_hash = None
    has_more = False

    count_photos_all = 0
    count_photos_limit = 0

    def __init__(self, filters):
        self.filters = filters

    @staticmethod
    def from_request(request):
        return ThumbnailPager(Filters.from_dict(request.REQUEST))

    @staticmethod
    def from_dict(vars):
        return ThumbnailPager(Filters.from_dict(vars))

    def load_page(self, limit=None):
        """
        Get one page of thumbnails for this set of filters. If last_hash is
        part of the filters, use only photos with a lower order_id.

        Get all photos by setting `limit=None`
        """
        log.info("ThumbailPager: load page with filters: %s" % str(self.filters))

        # Get the db query for these filters
        self.photo_query = filters_to_query(self.filters)
        self.photos = self.photo_query[:limit] if limit else self.photo_query

        # Save the counts
        self.count_photos_all = self.photo_query.count()
        self.count_photos_limit = self.photos.count()

        # Save the last hash
        if self.count_photos_limit:
            self.last_hash = self.filters.last_hash = self.photos[self.count_photos_limit-1].hash
        else:
            self.last_hash = self.filters.last_hash = None

        # Save whether there are more
        self.has_more = self.count_photos_all > self.count_photos_limit

        # All done
        return self
