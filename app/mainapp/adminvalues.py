"""
AdminValues are settings which can have the default (eg. in settings.py)
but can be overwritten by creating a models.AdminValue object with the
specified key.

Source code must simply reference adminvalues.AdminValues.ADMINVALUE_VAR instead
of a hard-coded setting.
"""
import mainapp.models as models
from django.conf import settings


class AdminValues(object):
    """
    Helper to get the AdminValues or the default.
    """
    # Add any fields here that you wish.
    # ADMINVALUE_VAR = (models.AdminValue.key, default_obj=None)
    PHOTOFLOW_LAYOUTS = ("photoflow_layouts", [0])
    PHOTOFLOW_LAYOUTS_TEST = ("photoflow_layouts_test", [0])

    PHOTOGRID_ITEMS_INITIAL = ("photogrid_items_initial", settings.PHOTOGRID_ITEMS_INITIAL)
    PHOTOGRID_ITEMS_PERPAGE = ("photogrid_items_perpage", settings.PHOTOGRID_ITEMS_PERPAGE)

    PHOTOFLOW_BLOCKS_INITIAL = ("photoflow_blocks_initial", settings.PHOTOFLOW_BLOCKS_INITIAL)
    PHOTOFLOW_BLOCKS_PERPAGE = ("photoflow_blocks_perpage", settings.PHOTOFLOW_BLOCKS_PERPAGE)

    @staticmethod
    def get(key):
        """
        Returns the value of the models.AdminValue object if it exists, else
        returns the hard-coded default value.
        """
        if isinstance(key, tuple):
            db_key, default = key
        else:
            if not hasattr(AdminValues, key):
                raise AttributeError("AdminValue with key '%s' not found.")
            db_key, default = getattr(AdminValues, key)

        try:
            return models.AdminValue.objects.get(key=db_key).val
        except models.AdminValue.DoesNotExist:
            return default
