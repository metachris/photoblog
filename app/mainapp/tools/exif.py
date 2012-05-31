import json
import logging
import Image
from PIL.ExifTags import TAGS


log = logging.getLogger(__name__)


class ExifHolder(object):
    """
    Immediately loads all tags which are then serializeable.
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


if __name__ == "__main__":
    # Monkey patch to stdout logging
    log = logging

    # Do some exif testing
    exif = ExifHolder(Image.open("/opt/photosite/media/upload/789wqx.jpeg"))
    exif.get("DateTimeOriginal")
    print json.dumps(exif.values)
