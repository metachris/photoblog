import os
import shutil
import logging
import commands
from pprint import pprint

import Image
from PIL.ExifTags import TAGS

from django.conf import settings

import app.mainapp.models
import app.mainapp.tools

log = logging.getLogger(__name__)


DIR_UPLOAD_FULL = os.path.join(settings.MEDIA_ROOT, settings.MEDIA_DIR_UPLOAD)
DIR_PHOTOS_FULL = os.path.join(settings.MEDIA_ROOT, settings.MEDIA_DIR_PHOTOS)


def upload_photo(f):
    """
    Upload file to temp dir, use `file` to guess filetype, verify,
    then move to media/upload/, and finally resize and add to media/photos/.

    Returns the filename of the image without path prefix
    """
    uploader = PhotoUploader(f)
    return uploader.upload()


class PhotoUploader(object):
    hash = None
    ext = None

    def __init__(self, file_upload):
        """file_upload parameter is a django FileUpload object from request.FILES"""
        log.info("Photo upload: %s" % file_upload)
        self.f = file_upload
        self.fn_tmp = "/tmp/%s" % app.mainapp.tools.id_generator(16)

    def upload(self):
        """Perform upload process and return filename"""
        self.upload_via_http()
        self.ext = self.verify_uploaded_image()
        self.process_verified_image()
        return self.get_filename()

    def upload_via_http(self):
        # Upload to temp dir
        tmpfile = open(self.fn_tmp, "w")
        for chunk in self.f.chunks():
            tmpfile.write(chunk)
        tmpfile.close()

    def verify_uploaded_image(self):
        """
        Make sure it's a valid image and return detected filetype (file extension).
        Returns one string which is the detected filetype (eg. "jpeg" or "png")
        """
        # First filetype check with `file`
        filetype = commands.getoutput("file -b %s" % self.fn_tmp)
        if not "JPEG" in filetype and not "PNG" in filetype:
            raise TypeError("Unsupported filetype for upload %s: %s" % (self.f, filetype))

        # Second filetype check with PIL.
        try:
            im = Image.open(self.fn_tmp)
            im.verify()
        except Exception as e:
            print e
            raise TypeError("PIL could not verify image (%s)" % self.f)

        # Show some image infos
        print im.format, im.size, im.mode
        pprint(get_exif(im))

        # Valid image
        ext = im.format.lower()
        return ext

    def get_filename(self):
        if not self.hash:
            self.hash = app.mainapp.models.Photo._mk_hash()
        return "%s.%s" % (self.hash, self.ext)

    def process_verified_image(self):
        fn = self.get_filename()

        # Move original to /media/upload/<filename>
        fn_upload = os.path.join(DIR_UPLOAD_FULL, fn)
        shutil.move(self.fn_tmp, fn_upload)
        log.info("- added %s" % fn_upload)

        # Resize
        im = Image.open(fn_upload)
        width, height = im.size
        is_portrait = height > width
        if is_portrait:
            target_size = 1080, 1920
        else:
            target_size = 1920, 1080

        print "- building thumbnail in target size (width, height): %s..." % (str(target_size))
        im.thumbnail(target_size, Image.ANTIALIAS)
        print "- built"

        # Save to /media/photos/<hash>.<ext(jpg|png)>
        fn_photo = os.path.join(DIR_PHOTOS_FULL, fn)
        print "Saving... to %s" % fn_photo
        im.save(fn_photo)
        print "saved"

        # - Add copyright exif tag (TODO)


def get_exif(image):
    ret = {}
    info = image._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret
