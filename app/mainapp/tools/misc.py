import re
import os
import shutil
import unicodedata
import string
import random
import commands
import logging
import Image
from PIL.ExifTags import TAGS


from django.conf import settings


log = logging.getLogger(__name__)


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-ascii characters,
    and converts spaces to hyphens.

    From Django's "django/template/defaultfilters.py".
    """
    _slugify_strip_re = re.compile(r'[^\w\s-]')
    _slugify_hyphenate_re = re.compile(r'[-\s]+')

    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_hyphenate_re.sub('-', value)


def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def upload_photo(f):
    """
    Upload file to temp dir, use `file` to guess filetype, and
    then move to media dir.
    """
    log.info("Photo upload: %s" % f)
    DIR_UPLOAD = "upload"
    DIR_ORIG = "photos"

    # Upload to temp dir
    fn_tmp = "/tmp/%s" % id_generator(16)
    f_out = open(fn_tmp, "w")
    for chunk in f.chunks():
        f_out.write(chunk)
    f_out.close()

    # Try to guess file type
    filetype = commands.getoutput("file -b %s" % fn_tmp)
    if "JPEG" in filetype:
        ext = "jpg"
    elif "PNG" in filetype:
        ext = "png"
    else:
        raise TypeError("Unsupported filetype: %s" % filetype)

    # Move image
    dir_to = os.path.join(settings.MEDIA_ROOT, DIR_UPLOAD)
    fn_to = None
    while not fn_to or os.path.isfile(fn_to):
        hash = id_generator(6)
        fn_to = os.path.join(dir_to, "%s.%s" % (hash, ext))

    shutil.move(fn_tmp, fn_to)
    log.info("- added %s" % fn_to)

    # Detect some image properties and show exif tags
    im = Image.open(fn_to)
    print im.format, im.size, im.mode
    print get_exif(im)

    # Now last step: build the 'original':
    # - Compress a bit stronger
    # - Scale down if too large
    # - Add copyright exif tag

    return (hash, ext)


def get_exif(image):
    ret = {}
    info = image._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret
