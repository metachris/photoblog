"""
Helper to build photo flows.

Html uses container divs for all columns and places image divs inside.

Todo: Cache based on photo-query-hash + layouts-used
"""
import hashlib
from django.template.context import Context
from django.template.loader import get_template
from mainapp import models

from django.core.cache import cache

from mainapp import adminvalues


FLOW_LAYOUTS = [
    # | 1 2 2 2 | 2 columns: 1x2, 3x2
    # | 1 2 2 2 |
    ({ "item": "1x2" }, { "item": "3x2" }),

    # | 1 1 2 3 | 3 columns: 2x2, 1x2, 1x1 + 1x1
    # | 1 1 2 4 |
    ({ "item": "2x2" }, { "item": "1x2" }, { "items": ["1x1", "1x1"], "size": "1x2" }),

    ({ "items": ["1x1", "1x1"], "size": "1x2" }, { "item": "1x2" }, { "item": "2x2" }),
    ({ "item": "3x2" }, { "items": ["1x1", "1x1"], "size": "1x2" }),

    # | 1 2 2 5 | 3 columns: 1x2, 2x1 + 1x1 + 1x1, 1x2
    # | 1 3 4 5 |
    ({ "item": "1x2" }, { "items": ["2x1", "1x1", "1x1"], "size": "2x2" }, { "item": "1x2"}),

    # | 1 3 3 4 | 3 columns: 1x1 + 1x1, 2x2, 1x1 + 1x1
    # | 2 3 3 5 |
    ({ "items": ["1x1", "1x1"], "size": "1x2" }, { "item": "2x2"}, { "items": ["1x1", "1x1"], "size": "1x2" }),
]

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

class Renderer(object):
    """
    Builds a list of columns based on the supplied photos and chosen layouts.
    """
    # Counters
    cur_col = 0
    cur_item = 0

    # Helpers for max-blocks (1 block is 4x2)
    max_blocks = None
    cur_block = 0
    cur_block_col = 0

    # Current layout
    layout = None

    # Temporary
    cols = []
    items_tmp = []

    # public
    photo_count = 0

    def __init__(self, layout_ids, max_blocks=None):
        """
        layout_ids is a list of FLOW_LAYOUTS indexes. If max_blocks is
        supplied, self.build_cols will return at most that number of blocks.
        """
        if not isinstance(layout_ids, list):
            raise ValueError("Renderer requires a list of layout_ids. Got: '%s'" % repr(layout_ids))
        self.max_blocks = max_blocks
        self.layout = []
        for id in layout_ids:
            self.layout += FLOW_LAYOUTS[id]

    def build_cols(self, photos, col_offset=0):
        """
        Build the columns with the supplied photos. Layout starts at col_offset.
        Returns the list of columns.
        """
        self.cur_col = col_offset % len(self.layout)
        self.cur_item = 0
        self.cols = []
        self.items_tmp = []
        for photo in photos:
            is_finished = self.add_item(photo)
            if is_finished:
                return self.cols

        self.finish_adding()
        return self.cols

    def add_item(self, photo):
        """
        Add a single photo into the current div-column. Returns True if
        max-blocks has been reached and the current columns can be directly
        returned.
        """
        # Get the current column's schema definition
        cur_col = self.layout[self.cur_col]
        if "item" in cur_col:
            # If only one item in this column, we need no additional params
            col_itemsschemas = [cur_col["item"]]
            col_size = cur_col["item"]
        else:
            col_size = cur_col["size"]
            col_itemsschemas = cur_col["items"]

        # Add the new item to the temporary list
        cur_itemschema = col_itemsschemas[self.cur_item]
        w, h = cur_itemschema.split("x")
        self.items_tmp.append(Item(photo, int(w), int(h)))

        # Keep some counters
        self.photo_count += 1
        self.cur_item += 1

        if self.cur_item == len(col_itemsschemas):
            # End of current column reached. Save items as column
            col_w, col_h = col_size.split("x")
            self.cur_block_col += int(col_w)
            self.cols.append(Col(self.items_tmp, int(col_w), int(col_h)))
            self.items_tmp = []
            self.cur_item = 0

            # Break on max_blocks
            self.cur_col = (self.cur_col + 1) % len(self.layout)
            if self.cur_block_col % 4 == 0:
                self.cur_block += 1
                if self.cur_block == self.max_blocks:
                    return True

    def finish_adding(self):
        """Adds any tmp items as last column"""
        if len(self.items_tmp):
            cur_col = self.layout[self.cur_col]
            col_w, col_h = cur_col["size"].split("x")
            self.cols.append(Col(self.items_tmp, int(col_w), int(col_h)))

class FlowManager(object):
    """Helps with managing flow pages"""
    def __init__(self, layout_ids=None, is_test_layouts=False):
        """
        Sets the current layout based on models.AdminValue; if layout_ids list
        is supplied, use that instead.

        If is_test_layouts is True, use the LAYOUTS_TEST AdminValue instead of LAYOUTS.
        """
        self.is_test_layouts = is_test_layouts
        self.layout_ids = layout_ids or self.get_layout_ids()
        self.layout = []
        for id in self.layout_ids:
            self.layout.append(FLOW_LAYOUTS[id])

    def get_layout_ids(self):
        try:
            # This 'db' query is cached, so no need to worry about performance issues
            key = adminvalues.PHOTOFLOW_LAYOUTS_TEST if self.is_test_layouts else adminvalues.PHOTOFLOW_LAYOUTS
            layout_ids = [int(id) for id in models.AdminValue.objects.get(key=key).val.split(",")]
        except models.AdminValue.DoesNotExist:
            layout_ids = [0]
        return layout_ids

    def get_cols_per_block(self, block_index):
        """Get the number of columns for a specific block (0..n)"""
        n_actual = block_index % len(self.layout)
        return len(self.layout[n_actual])

    def get_items_per_block(self, block_index):
        """Get the number of photos for a specific block (0..n)"""
        n_actual = block_index % len(self.layout)
        count = 0
        for el in self.layout[n_actual]:
            count += 1 if "item" in el else len(el["items"])
        return count

    def get_html(self, photos, max_blocks=None, block_offset=0):
        """
        Get the flow-html for the supplied photos. If max_blocks is
        supplied get_html will return at most that number of blocks.
        If block_offset is specified, the layout starts at that block.
        """
    #    print layouts
    #    cache_key = "photo_flow:%s" % hashlib.sha256("%s%s" % (repr(layouts), photos.query)).hexdigest()
    #    print "Cache key:", cache_key
        # See if we can get that cached
        #    cached = cache.get(cache_key)
        #    if cached:
        #        print "Return cached"
        #        return cached


        # Compute col_offset based on block_offset
        col_offset = 0
        if block_offset:
            for i in xrange(block_offset):
                col_offset += self.get_cols_per_block(i)
        #print "block offset: %s (= col_offset: %s)" % (block_offset, col_offset)

        # Get the photos and build the flow
        flow_renderer = Renderer(layout_ids=self.layout_ids, max_blocks=max_blocks)
        cols = flow_renderer.build_cols(photos, col_offset=col_offset)

        # Render the flow into the template
        flow_template = get_template('mainapp/photoflow_item.html')
        html = flow_template.render(Context({ "cols": cols }))
    #    cache.set(cache_key, res, 60)
        return html
