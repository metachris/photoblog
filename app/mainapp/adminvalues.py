"""
Settings which can have a local default (eg. from settings.py, ...) but can be
overwritten by creating a models.AdminValue object with the specified key (eg.
in the Django admin interface).

Source code must simply reference adminvalues.YOUR_VALUE instead
of a hard-coded setting.
"""
import mainapp.models as models
from django.conf import settings


class AdminValue(object):
    """ Simple AdminValue Container """
    def __init__(self, db_key, default=None):
        self.db_key = db_key
        self.default = default


# AdminValue declarations. Add any fields that you want here.
PHOTOFLOW_LAYOUTS = AdminValue("photoflow_layouts", "0")
PHOTOFLOW_LAYOUTS_TEST = AdminValue("photoflow_layouts_test", "0")

PHOTOGRID_ITEMS_INITIAL = AdminValue("photogrid_items_initial", settings.PHOTOGRID_ITEMS_INITIAL)
PHOTOGRID_ITEMS_PERPAGE = AdminValue("photogrid_items_perpage", settings.PHOTOGRID_ITEMS_PERPAGE)

PHOTOFLOW_BLOCKS_INITIAL = AdminValue("photoflow_blocks_initial", settings.PHOTOFLOW_BLOCKS_INITIAL)
PHOTOFLOW_BLOCKS_PERPAGE = AdminValue("photoflow_blocks_perpage", settings.PHOTOFLOW_BLOCKS_PERPAGE)


def get(av):
    """
    Returns the value of the models.AdminValue object if it exists, else
    returns the hard-coded default value.

    Example usage: adminvalues.get(adminvalues.PHOTOFLOW_LAYOUTS)
    """
    try:
        ret = models.AdminValue.objects.get(key=av.db_key, enabled=True).val
    except models.AdminValue.DoesNotExist:
        ret = av.default

    # print "AdminValues: '%s' = '%s'" % (av.db_key, ret)
    return ret


def get_int(av):
    """Return an int (force cast)"""
    return int(get(av))
