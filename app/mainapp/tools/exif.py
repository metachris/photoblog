import json
import logging
import Image
import commands
from PIL.ExifTags import TAGS
from pprint import pprint

log = logging.getLogger(__name__)


class ExifToolHolder(object):
    """
    Exif info holder via `exiftool`
    """
    values = {}

    def __init__(self, fn):
        self.values = json.loads(commands.getoutput("exiftool -json %s" % fn))[0]

    def get(self, key, default=None):
        return self.values.get(key, default)


if __name__ == "__main__":
    # Do some exif testing
    pass

    #exif = ExifToolHolder("/opt/photosite/media/upload/789wqx.jpeg")
    #pprint(exif.values)
