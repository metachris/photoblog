import os
import shutil
import logging

import Image

from django.conf import settings

import app.mainapp.models
import app.mainapp.tools
from app.mainapp.tools.exif import ExifToolHolder


log = logging.getLogger(__name__)


# Target resolution
RES_HD_1080 = (1920, 1080)
#RES_XXL_1440 = (2560, 1440)

# Whether processed photos should always be stored as jpeg or in their native format.
ALWAYS_OUTPUT_JPEG = True

# 90: 21mb->6mb
PHOTO_QUALITY_VALUE = 80

# Exif tags to copy from the uploaded onto the preprocessed image (if set)
EXIF_TAGS_COPY = ['ApertureValue', 'Caption-Abstract', 'Copyright',
        'CreateDate', 'DateTimeOriginal', 'Exposure', 'ExposureTime',
        'FNumber', 'Flash', 'FocalLength', 'FocalLengthIn35mmFormat',
        'ISO', 'ImageDescription', 'Lens', 'LensInfo', 'LensModel', 'Make',
        'Model', 'ShutterSpeedValue']

# Jpeg file comment
EXIF_COMMENT = "Photo ID: {photo_id}. Copyright (c) %s. You can find this photo online at http://www.chrishager.at" % settings.EXIF_COPYRIGHT_TAG

# Internal shortcuts
DIR_UPLOAD_FULL = os.path.join(settings.MEDIA_ROOT, settings.MEDIA_DIR_UPLOAD)
DIR_PHOTOS_FULL = os.path.join(settings.MEDIA_ROOT, settings.MEDIA_DIR_PHOTOS)


class PhotoUploader(object):
    """
    Photo uploader, preprocessor (with PIL) and info collector.

    All exif info from the uploaded file will be stored in self.exif;
    the preprocessed jpeg file will only posess the specified subset of
    exif tags.
    """
    # All these values will be added during the upload process
    hash = None    # Unique hash for this photo
    exif = {}      # Uploaded photo's exif info
    ext = None     # `jpeg` if ALWAYS_OUTPUT_JPEG else native format
    format = None  # native format (eg. `jpeg` or `png`)

    fn_form = None   # Filename supplied with the html form
    fn_upload = None # in /upload/... Keeps original format


    # Target size (specified res, perhaps switched if portrait mode)
    target_width = None
    target_height = None

    # Info about uploaded file
    upload_width = None
    upload_height = None

    # Info about preprocessed base image
    photo_width = None
    photo_height = None

    def __init__(self, file_upload, hash=None):
        """
        - file_upload parameter is a django FileUpload object from request.FILES
        - if hash is given, use that for filenames instead of a newly created one
        """
        log.info("Photo upload: %s" % file_upload)
        self.f = file_upload
        self.hash = hash
        self.fn_form = str(file_upload)
        self.fn_tmp = "/tmp/%s" % app.mainapp.tools.id_generator(16)

    def upload(self, target_resolution=RES_HD_1080):
        """Perform upload process"""
        self.target_width, self.target_height = target_resolution
        self.upload_via_http()
        self.verify_uploaded_image()
        self.process_verified_image()

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
        log.info("- verify")
        # First filetype check with `file`
        try:
            im = Image.open(self.fn_tmp)
            im.verify()
        except Exception as e:
            log.error("PIL could not verify image (%s): %s" % (self.f, e))
            raise TypeError("PIL could not verify image (%s)" % self.f)

        # Valid image. Save infos
        self.format = im.format
        self.ext = "jpeg" if ALWAYS_OUTPUT_JPEG else self.format.lower()

    def process_verified_image(self):
        if not self.hash:
            self.hash = app.mainapp.models.Photo._mk_hash()

        # Move original to /media/upload/<filename>.<ext-orig>
        self.fn_upload = "%s.%s" % (self.hash, self.format.lower())
        self.fn_upload_full = os.path.join(DIR_UPLOAD_FULL, self.fn_upload)
        shutil.move(self.fn_tmp, self.fn_upload_full)
        log.info("- added %s" % self.fn_upload_full)

        # Add copyright exif tag to uploaded image
        os.system("""exiftool -overwrite_original "-EXIF:Copyright=%s" %s""" % (settings.EXIF_COPYRIGHT_TAG, self.fn_upload_full))

        # Load exif infos for local access
        self.exif = ExifToolHolder(self.fn_upload_full)

        # Resize
        im = Image.open(self.fn_upload_full)
        self.upload_width, self.upload_height = im.size

        # Switch target resolution w+h if portrait
        if self.upload_height > self.upload_width:
            self.target_width, self.target_height = self.target_height, self.target_width

        # Resize
        log.info("- want: resizing from orig(%s) to target(%s, %s)" % (str(im.size), self.target_width, self.target_height))
        im.thumbnail((self.target_width, self.target_height), Image.ANTIALIAS)
        self.photo_width, self.photo_height = im.size
        log.info("- resized. final photo size: %s" % str(im.size))

        # Save to /media/photos/<hash>.<ext(jpg|png)>
        self.fn_photo = "%s.%s" % (self.hash, self.ext)
        self.fn_photo_full = os.path.join(DIR_PHOTOS_FULL, self.fn_photo)
        log.info("- saving to %s..." % self.fn_photo_full)
        im.save(self.fn_photo_full, quality=PHOTO_QUALITY_VALUE)
        log.info("- saved. copying exif tags...")

        # - Copy specified exif tags
        comment = EXIF_COMMENT.format(photo_id=self.hash)
        tags = ' '.join(['"-EXIF:%s=%s"' % (tag, self.exif.get(tag)) for tag in EXIF_TAGS_COPY if self.exif.get(tag)])
        cmd = """exiftool -overwrite_original "-Comment=%s" %s %s""" % (comment, tags, self.fn_photo_full)
        os.system(cmd)
        log.info("- all done")
