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
from app.mainapp.tools.exif import ExifHolder


log = logging.getLogger(__name__)


DIR_UPLOAD_FULL = os.path.join(settings.MEDIA_ROOT, settings.MEDIA_DIR_UPLOAD)
DIR_PHOTOS_FULL = os.path.join(settings.MEDIA_ROOT, settings.MEDIA_DIR_PHOTOS)

RES_HD_1080 = (1920, 1080)

class PhotoUploader(object):
    """
    Photo uploader, preprocessor (with PIL) and info collector
    """
    # All these values will be added during the upload process
    hash = None
    ext = None
    exif = {}

    # Info about uploaded file
    upload_width = None
    upload_height = None

    # Target size
    target_width = None
    target_height = None

    # Info about preprocessed base image
    photo_width = None
    photo_height = None

    def __init__(self, file_upload, target_resolution=RES_HD_1080):
        """file_upload parameter is a django FileUpload object from request.FILES"""
        log.info("Photo upload: %s" % file_upload)
        self.f = file_upload
        self.fn_tmp = "/tmp/%s" % app.mainapp.tools.id_generator(16)
        self.target_width, self.target_height = target_resolution

    def upload(self):
        """Perform upload process and return filename"""
        self.upload_via_http()
        self.verify_uploaded_image()
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
        log.info("- verify")
        filetype = commands.getoutput("file -b %s" % self.fn_tmp)
        if not "JPEG" in filetype and not "PNG" in filetype:
            print e
            raise TypeError("Unsupported filetype for upload %s: %s" % (self.f, filetype))

        log.info("- verify 2")
        # Second filetype check with PIL.
        try:
            im = Image.open(self.fn_tmp)
            im.verify()
        except Exception as e:
            print e
            raise TypeError("PIL could not verify image (%s)" % self.f)

        # Valid image. Save infos
        self.ext = im.format.lower()
        self.exif = ExifHolder(im)

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
        self.upload_width, self.upload_height = im.size

        # Switch target resolution w+h if portrait
        if self.upload_height > self.upload_width:
            self.target_width, self.target_height = self.target_height, self.target_width

        log.info("- resizing from orig(%s) to target(%s, %s)" % (str(im.size), self.target_width, self.target_height))
        im.thumbnail((self.target_width, self.target_height), Image.ANTIALIAS)
        self.photo_width, self.photo_height = im.size
        log.info("- resized. final photo size: %s" % str(im.size))

        # Save to /media/photos/<hash>.<ext(jpg|png)>
        fn_photo = os.path.join(DIR_PHOTOS_FULL, fn)
        log.info("- saving to %s..." % fn_photo)
        im.save(fn_photo)
        log.info("- saved")

        # - Add copyright exif tag (TODO)
