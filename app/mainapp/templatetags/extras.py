# encoding: utf-8
import datetime
from django import template
from django.template.context import Context
from django.template.defaultfilters import stringfilter
from django.template.defaultfilters import date as date_filter
from django.core.cache import cache
from django.template.loader import get_template

import mainapp.forms

register = template.Library()


@register.filter
def split(val, separator=" "):
    return (v for v in val.split(separator) if v)


def _photo_title(photo, prefix="", apostrophes=True, capitalized=False):
    """Compose a photo title or return default for photos without title"""
    default = "Untitled %shoto" % ("p" if not capitalized else "P")
    wanted = "{prefix}'{photo.title}'" if apostrophes else "{prefix}{photo.title}"
    return wanted.format(prefix=prefix, photo=photo) if photo.title else default


@register.filter
def photo_title(photo, apostrophes=False, capitalized=True):
    return _photo_title(photo, apostrophes=apostrophes, capitalized=capitalized)


@register.filter
def photo_alt(photo):
    """Format photo alt html info"""
    key = "photo-alt:%s" % photo.id

    # See if we can get that cached
    cached = cache.get(key)
    if cached:
        return cached

    # Else build, cache and return
    ret = _photo_title(photo, prefix="Photo ")
    if (photo.photographer and photo.photographer.name) or \
            photo.date_captured or photo.location:
        ret += ", captured"
    if photo.photographer and photo.photographer.name:
        ret += " by {photo.photographer.name}"
    if photo.date_captured:
        ret += " on %s" % date_filter(photo.date_captured)
    if photo.location:
        ret += " in {photo.location.name}"
    ret = ret.format(photo=photo).replace('"', "'")
    cache.set(key, ret, 60)
    return ret


@register.filter
def photo_exif_shot(photo):
    """Format photo exif info"""
    ret = u""
    if photo.exif_exposuretime or photo.exif_aperture or \
            photo.exif_iso or photo.exif_focallength:
        if photo.exif_exposuretime:
            if "/" in photo.exif_exposuretime:
                # format for html fraction
                time = photo.exif_exposuretime.split("/")
                ret += "<big><sup>%s</sup>&frasl;<sub>%s</sub> </big>sec" % \
                       (time[0], time[1])
            else:
                ret += "{photo.exif_exposuretime} sec"
            if photo.exif_aperture:
                ret += " at "
        if photo.exif_aperture:
            ret += u"ƒ {photo.exif_aperture}"
        if photo.exif_iso:
            if ret:
                ret += ", "
            ret += "ISO {photo.exif_iso}"
        if photo.exif_focallength:
            if ret:
                ret += ", "
            ret += "{photo.exif_focallength}"
        ret = ret.format(photo=photo)
        ret = "<p>%s</p>" % ret
    return ret


@register.filter
def build_flow(photos):
    """Build photo flow tables"""
    TD_WIDTH = 220  # 4 cols = 880 px
    TD_HEIGHT = 220
    PADDING_HORIZ = 14 + 2 # 2px border
    PADDING_VERT = 14 + 2  # 2px border
    class Item:
        photo = None
        w = 0  # number of tds
        h = 0  # number of tds
        td_w = 0  # px width of td
        td_h = 0  # px height of td
        img_size = ""  # WxH
        def __init__(self, photo, w, h):
            self.photo = photo;
            self.w = w; self.h = h

            self.td_w = TD_WIDTH * w
            self.td_h = TD_HEIGHT * h

            img_w = self.td_w - PADDING_HORIZ
            img_h = self.td_h - PADDING_VERT
            self.size = "%sx%s" % (img_w, img_h)

    n = len(photos)
    print "flow for ", n, "photos"

    rows = []

    # Build 1st row
    items = []
    items.append(Item(photos[0], 1, 2))  # left col, 2 rows
    items.append(Item(photos[1], 2, 1))  # 1st row, cols 2+3
    items.append(Item(photos[2], 1, 2))  # right col, 2 rows
    rows.append(items)

    # Build 2nd row
    items = []
    items.append(Item(photos[3], 2, 1))  # 2nd row, cols 2+3
    rows.append(items)

    print "rows"
    print rows

    flow_template = get_template('mainapp/photoflow_item.html')
    res = flow_template.render(Context({ "rows": rows }))
    return res

# Decide on a schema inside an 8 cols, 2 rows table (WxH, XxY)
    #
    # Test schema:  1 2 2 4
    #               1 3 3 4
    #

    return ["hi"]
