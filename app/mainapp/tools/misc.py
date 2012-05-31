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
from pprint import pprint

from django.conf import settings
import app.mainapp.models


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
    Upload file to temp dir, use `file` to guess filetype, verify,
    then move to media/upload/, and finally resize and add to media/photos/.
    """
    log.info("Photo upload: %s" % f)
    DIR_UPLOAD = "upload"  # origs with exif, full res
    DIR_PHOTOS = "photos"  # pre-processed origs, HD resolution

    dir_upload_full = os.path.join(settings.MEDIA_ROOT, DIR_UPLOAD)
    dir_photos_full = os.path.join(settings.MEDIA_ROOT, DIR_PHOTOS)
    fn_tmp = "/tmp/%s" % id_generator(16)

    # Upload to temp dir
    f_out = open(fn_tmp, "w")
    for chunk in f.chunks():
        f_out.write(chunk)
    f_out.close()

    # First filetype check with `file`
    filetype = commands.getoutput("file -b %s" % fn_tmp)
    if not "JPEG" in filetype and not "PNG" in filetype:
        raise TypeError("Unsupported filetype: %s" % filetype)

    # Second filetype check with PIL.
    try:
        im = Image.open(fn_tmp)
        im.verify()
    except Exception:
        raise TypeError("PIL could not verify image (%s)" % f)

    # Valid image. Create extension and unique hash
    ext = im.format.lower()
    hash = app.mainapp.models.Photo._mk_hash()

    # Move original to /media/upload/<hash>.<ext>
    fn_upload = os.path.join(dir_upload_full, "%s.%s" % (hash, ext))
    shutil.move(fn_tmp, fn_upload)
    log.info("- added %s" % fn_upload)

    # Show some image infos
    print im.format, im.size, im.mode
    pprint(get_exif(im))

#    for tag in exif:
#        print "- %s:" % (tag)
#        try:
#            info = str(exif[tag])
#            print info[:100]
#        except:
#            print "Exception"

    # Resize for final 'orig' img
    width, height = im.size
    is_portrait = height > width
    if is_portrait:
        target_size = 1080, 1920
    else:
        target_size = 1920, 1080

    print "- building thumbnail in target size (width, height): %s..." % (str(target_size))
    im2 = Image.open(fn_upload)
    im2.thumbnail(target_size, Image.ANTIALIAS)
    print "- built"

    # Save to /media/photos/<hash>.<ext(jpg|png)>
    fn_photo = os.path.join(dir_photos_full, "%s.%s" % (hash, ext))
    print "Saving... to %s" % fn_photo
    im2.save(fn_photo)
    print "saved"

    # - Add copyright exif tag (TODO)
    return (hash, ext)


def get_exif(image):
    ret = {}
    info = image._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret
