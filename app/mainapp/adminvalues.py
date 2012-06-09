"""
AdminValues are settings which can have the default (eg. in settings.py)
but can be overwritten by creating a models.AdminValue object with the
specified key.

Source code must simply reference adminvalues.AdminValues.ADMINVALUE_VAR instead
of a hard-coded setting.
"""
import mainapp.models as models
from django.conf import settings


# Add any fields here that you wish.
# ADMINVALUE_VAR = (models.AdminValue.key, default_obj=None)
PHOTOFLOW_LAYOUTS = ("photoflow_layouts", [0])
PHOTOFLOW_LAYOUTS_TEST = ("photoflow_layouts_test", [0])

PHOTOGRID_ITEMS_INITIAL = ("photogrid_items_initial", settings.PHOTOGRID_ITEMS_INITIAL)
PHOTOGRID_ITEMS_PERPAGE = ("photogrid_items_perpage", settings.PHOTOGRID_ITEMS_PERPAGE)

PHOTOFLOW_BLOCKS_INITIAL = ("photoflow_blocks_initial", settings.PHOTOFLOW_BLOCKS_INITIAL)
PHOTOFLOW_BLOCKS_PERPAGE = ("photoflow_blocks_perpage", settings.PHOTOFLOW_BLOCKS_PERPAGE)


def get(key):
    """
    Returns the value of the models.AdminValue object if it exists, else
    returns the hard-coded default value.

    key needs to be a tuple of (<db_key>, <default>.

    Use like this: adminvalues.get(adminvalues.PHOTOFLOW_LAYOUTS)
    """
    db_key, default = key

    try:
        ret = models.AdminValue.objects.get(key=db_key).val
    except models.AdminValue.DoesNotExist:
        ret = default

#    print "AdminValues: '%s' = '%s'" % (key, ret)
    return ret


def get_int(key):
    """Return an int (force cast)"""
    return int(get(key))
