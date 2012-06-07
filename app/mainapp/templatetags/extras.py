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
    """Build photo flow tables."""
    class Col:
        """One column of photos; rendered into one left-floating div. Computes the correct size in px."""
        items = []

        def __init__(self, item_list, w=None, h=None):
            """If w or h is None, get it from the first image"""
            self.items = item_list
            if w is None or h is None:
                if len(items) == 1:
                    w = w or item_list[0].w
                    h = h or item_list[0].h
                else:
                    raise AttributeError("Class col requires exactly one item to auto-compute width and hight (got %s)." % len(item_list))

            self.w = w
            self.h = h

            # Calculate extra h+w (margin, border)
            frame_top, frame_right, frame_bottom, frame_left = Item.FRAME_SIZE
            w_extra = self.w * (Item.MARGIN_RIGHT + frame_left + frame_right)
            h_extra = self.h * (Item.MARGIN_BOTTOM + frame_top + frame_bottom)

            # Compute total column container size
            self.w_px = (Item.DEF_WIDTH * self.w) + w_extra
            self.h_px = (Item.DEF_HEIGHT * self.h) + h_extra

        def __str__(self):
            return "<Col[%sx%s](%s items)" % (self.w, self.h, len(self.items))

    class Item:
        """One item in a specific row. Computes the correct size in px."""
        # Default width and height for one grid item
        DEF_WIDTH = 220
        DEF_HEIGHT = 260

        # Margin right and bottom of an image
        MARGIN_RIGHT = 13
        MARGIN_BOTTOM = 13

        # Frame size in px (top, right, bottom, left)
        FRAME_SIZE = (1, 1, 1, 1)

        # Set on init
        photo = None
        w = 0  # number of tds
        h = 0  # number of tds
        td_w = 0  # px width of td
        td_h = 0  # px height of td
        img_size = ""  # WxH

        def __init__(self, photo, w, h):
            """w and h in 'grid'-columns"""
            self.photo = photo;
            self.w = w; self.h = h

            frame_top, frame_right, frame_bottom, frame_left = Item.FRAME_SIZE
            w_extra = 0 if w < 2 else (w-1) * (Item.MARGIN_RIGHT + frame_left + frame_right)
            h_extra = 0 if h < 2 else (h-1) * (Item.MARGIN_BOTTOM + frame_left + frame_right)

            img_h = (self.DEF_HEIGHT * h) + h_extra
            img_w = (self.DEF_WIDTH * w) + w_extra
            self.size = "%sx%s" % (img_w, img_h)

    class Renderer:
        FLOW_LAYOUTS = [
            # 3 columns: 1x2, 2x1 + 1x1 + 1x1, 1x2
            ({ "size": "1x2", "items": ["1x2"]}, { "size": "2x2", "items": ["2x1", "1x1", "1x1"]}, { "size": "1x2", "items": ["1x2"]}),

            # 2 columns: 1x2, 1x3
            ({ "size": "1x2", "items": ["1x2"]}, { "size": "3x2", "items": ["3x2"]})
        ]

        cur_col = 0
        cur_item = 0

        layout = None

        cols = []
        items_tmp = []

        def add_item(self, photo):
            cur_col = self.layout[self.cur_col]
            col_size = cur_col["size"]
            col_itemsschemas = cur_col["items"]
            cur_itemschema = col_itemsschemas[self.cur_item]
            w, h = cur_itemschema.split("x")

            self.items_tmp.append(Item(photo, int(w), int(h)))

            self.cur_item += 1
            if self.cur_item == len(col_itemsschemas):
                # Write tmp items
                col_w, col_h = col_size.split("x")
                self.cols.append(Col(self.items_tmp, int(col_w), int(col_h)))
                self.items_tmp = []
                self.cur_item = 0
                self.cur_col = (self.cur_col + 1) % len(self.layout)

        def finish_adding(self):
            """Adds any tmp items as last column"""
            if len(self.items_tmp):
                cur_col = self.layout[self.cur_col]
                col_w, col_h = cur_col["size"].split("x")
                self.cols.append(Col(self.items_tmp, int(col_w), int(col_h)))

        def build_cols(self, photos, layouts=[0, 1]):
            self.layout = []
            for id in layouts:
                self.layout += self.FLOW_LAYOUTS[id]
            print self.layout

            for photo in photos:
                self.add_item(photo)
            self.finish_adding()
            return self.cols

    n = len(photos)
    print "flow for ", n, "photos"

    cols = Renderer().build_cols(photos[:7])
    print cols

    flow_template = get_template('mainapp/photoflow_item.html')
    res = flow_template.render(Context({ "cols": cols }))
    return res
