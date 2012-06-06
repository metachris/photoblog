import hashlib
import logging

from django.core.cache import cache
from django.conf import settings

import mainapp.models as models


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


def filters_to_query(filters, limit):
    """
    This method builds a QuerySet out of one  filters object
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

    query = query.order_by("-order_id")[:limit]  # +1 to see whether there are more
    return query

class ThumbnailPager(object):
    """
    Helper to move between pages
    """
    filters = None
    last_hash = None

    has_more = False
    photos = None

    def __init__(self, filters=Filters()):
        self.filters = filters

    @staticmethod
    def from_request(request):
        if request.method == 'GET':
            return ThumbnailPager(Filters.from_dict(request.GET))
        elif request.method == 'POST':
            return ThumbnailPager(Filters.from_dict(request.POST))

    @staticmethod
    def from_dict(vars):
        return ThumbnailPager(Filters.from_dict(vars))

    def load_page(self, photos_per_page=None):
        """
        Get one page of thumbnails for this set of filters.
        If last_hash is given, use all photos with order_id < that one
        """
        if not photos_per_page:
            photos_per_page = settings.PHOTOGRID_ITEMS_INITIAL

        # Get the db query for these filters
        log.info("ThumbailPager: load page with filters: %s" % str(self.filters))
        self.photo_query = filters_to_query(self.filters, limit=photos_per_page+1)

        count = self.photo_query.count()
        # Poor mans has-more: get 1 more than requested
        self.has_more = count > photos_per_page

        # Save photos (trim the extra item if needed)
        self.photos = self.photo_query[:photos_per_page]
        self.photos_count = count if count < photos_per_page else count-1

        # Save last photos hash
        if self.photos_count:
            self.last_hash = self.filters.last_hash = self.photos[self.photos_count-1].hash

        return self


