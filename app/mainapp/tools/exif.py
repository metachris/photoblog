import json
import logging
import Image
import commands
from PIL.ExifTags import TAGS
from pprint import pprint

log = logging.getLogger(__name__)


class ExifHolder(object):
    """
    Exif info holder via PIL
    """
    values = {}
    def __init__(self, image):
        if not image.format.lower() == "jpeg":
            return
        info = image._getexif()
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            try:
                self.values[decoded] = unicode(str(value))
            except Exception as e:
                log.warn("Could not decode exif tag '%s': %s" % (decoded, e))

    def get(self, key, default=None):
        return self.values.get(key, default)


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

    #exif = ExifHolder(Image.open("/opt/photosite/media/upload/789wqx.jpeg"))
    #exif.get("DateTimeOriginal")

    #exif = ExifToolHolder("/opt/photosite/media/upload/789wqx.jpeg")
    #pprint(exif.values)
