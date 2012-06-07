"""
Helper to build photo flows.

Html uses container divs for all columns and places image divs inside.

Todo: Cache based on photo-query-hash + layouts-used
"""
FLOW_LAYOUTS = [
    # | 1 2 2 2 | 2 columns: 1x2, 3x2
    # | 1 2 2 2 |
    ({ "item": "1x2" }, { "item": "3x2" }),

    # | 1 1 2 3 | 2 columns: 2x2, 1x2, 1x1 + 1x1
    # | 1 1 2 4 |
    ({ "item": "2x2" }, { "item": "1x2" }, { "items": ["1x1", "1x1"], "size": "1x2" }),

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

class Renderer:
    """
    Builds a list of columns based on the supplied photos and chosen layouts. Example usage:

        cols = photoflow.Renderer(layouts=[0, 1]).build_cols(photos[:7])

    """
    cur_col = 0
    cur_item = 0

    layout = None

    cols = []
    items_tmp = []

    def __init__(self, layout_ids):
        """layout_ids is a LIST of FLOW_LAYOUTS indexes"""
        if not isinstance(layout_ids, list):
            raise ValueError("Renderer requires a list of layout_ids. Got: '%s'" % repr(layout_ids))
        self.layout = []
        for id in layout_ids:
            self.layout += FLOW_LAYOUTS[id]

    def build_cols(self, photos):
        """Build the columns with the supplied photos. Returns the columns list"""
        for photo in photos:
            self.add_item(photo)
        self.finish_adding()
        return self.cols

    def add_item(self, photo):
        """Add a single photo into the current div-column"""
        cur_col = self.layout[self.cur_col]
        if "item" in cur_col:
            # If only one item in this column, we need no additional params
            col_itemsschemas = [cur_col["item"]]
            col_size = cur_col["item"]
        else:
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
