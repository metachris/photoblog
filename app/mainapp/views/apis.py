from django.http import HttpResponse
import mainapp.models as models
from django.template.context import Context
from django.template.loader import get_template


PHOTOS_PER_PAGE = 2


class Filters(object):
    tags = None  # list of tag slugs
    sets = None  # list of set slugs
    location = None  # location slug
    featured_only = None

    # For paging
    last_hash = None

    keys = ["tags", "sets", "location", "featured_only", "last_hash"]

    def __init__(self, *args, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])

    @staticmethod
    def from_dict(vars):
        ret = Filters()
        ret.last_hash = vars.get("last_hash") or None
        ret.location = vars.get("location") or None
        if vars.get("featured_only") is not None:
            ret.featured = vars.get("featured-only")
        if vars.get("tags"):
            ret.tags = vars.get("tags").split("+")
        if vars.get("sets"):
            ret.sets = vars.get("sets").split("+")
        return ret

    def to_dict(self):
        return { k: getattr(self, k) for k in self.keys }

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


class ThumbnailPager(object):
    """
    Helper to move between pages
    """
    filters = None
    last_hash = None

    has_more = False
    photos = None

    def __init__(self, filters):
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

    def load_page(self):
        """
        Get one page of thumbnails for this set of filters.
        If last_hash is given, use all photos with order_id < that one
        """
        # Get the db query for these filters
        print "filters:", str(self.filters)
        self.photo_query = self._build_query()

        # Poor mans has-more: get 1 more than requested
        self.has_more = self.photo_query.count() > PHOTOS_PER_PAGE

        # Save photos (trim the extra item if needed)
        self.photos = self.photo_query[:PHOTOS_PER_PAGE]
        self.photos_count = self.photos.count()

        # Save last photos hash
        if self.photos_count:
            self.last_hash = self.filters.last_hash = self.photos[self.photos_count-1].hash

    def _build_query(self):
        """
        This method builds a QuerySet out of one image filters object
        """
        query = models.Photo.objects.filter(published=True)

        if self.filters.last_hash:
            photo_last = models.Photo.objects.get(hash=self.filters.last_hash)
            query = query.filter(order_id__lt=photo_last.order_id)

        if self.filters.featured_only:
            query = query.filter(featured=True)

        if self.filters.tags:
            # These tags and all their descendants
            tags = []
            for tag_slug in self.filters.tags:
                tag = models.Tag.objects.get(slug=tag_slug)
                tags += [tag]
                tags += tag.get_descendants()
            query = query.filter(tags__in=tags)

        if self.filters.sets:
            # These sets and all their descendants
            sets = []
            for set_slug in self.filters.sets:
                _set = models.Set.objects.get(slug=set_slug)
                sets += [_set]
                sets += _set.get_descendants()
            query = query.filter(sets__in=sets)

        if self.filters.location:
            query = query.filter(location=self.filters.location)

        query = query.order_by("-order_id")[:PHOTOS_PER_PAGE+1]  # +1 to see whether there are more
        #print query.query
        return query

