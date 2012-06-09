"""
Settings which can have a local default (eg. from settings.py, ...) but may be
overwritten by creating a models.AdminValue object with the specified key (eg.
in the Django admin interface). Example usages:

    >>> adminvalues.PHOTOFLOW_LAYOUTS.get()
    >>> adminvalues.AdminValue("my_db_key", default=-1).get()
    >>> adminvalues.AdminValue("my_db_key").get()  # Will return default=None if not found in DB
"""
import mainapp.models as models
from django.conf import settings


class AdminValue(object):
    value = None
    has_updated = False

    def __init__(self, db_key, default=None):
        self.db_key = db_key
        self.default = default

    def get(self):
        """
        Returns the value of the models.AdminValue object if it exists, else
        returns the default value.
        """
        if not self.has_updated:
            try:
                self.value = models.AdminValue.objects.get(key=self.db_key, enabled=True).val
            except models.AdminValue.DoesNotExist:
                self.value = self.default
            self.has_updated = True
        #print "AdminValue '%s': '%s'" % (self.db_key, self.value)
        return self.value

    def get_int(self):
        """
        Casts any return value except `None` and `False` as integer
        """
        ret = self.get()
        return ret if ret is None or ret is False else int(ret)


# AdminValue declarations. Add any fields that you want here.
PHOTOFLOW_LAYOUTS = AdminValue("photoflow_layouts", "0")
PHOTOFLOW_LAYOUTS_TEST = AdminValue("photoflow_layouts_test", "0")

PHOTOGRID_ITEMS_INITIAL = AdminValue("photogrid_items_initial", settings.PHOTOGRID_ITEMS_INITIAL)
PHOTOGRID_ITEMS_PERPAGE = AdminValue("photogrid_items_perpage", settings.PHOTOGRID_ITEMS_PERPAGE)

PHOTOFLOW_BLOCKS_INITIAL = AdminValue("photoflow_blocks_initial", settings.PHOTOFLOW_BLOCKS_INITIAL)
PHOTOFLOW_BLOCKS_PERPAGE = AdminValue("photoflow_blocks_perpage", settings.PHOTOFLOW_BLOCKS_PERPAGE)
