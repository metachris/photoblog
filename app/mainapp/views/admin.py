import os
import datetime
import json
from pprint import pprint
import logging
import urllib

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib.auth.models import User
from django.contrib import auth
from django.core import exceptions
from django.template.loader import get_template
from django.template import Context, Template
from django.core.cache import cache

from django.conf import settings

import mainapp.models as models
import mainapp.forms as forms
import mainapp.tools as tools
import mainapp.tools.sendmail as sendmail
import mainapp.tools.mailchimp as mailchimp
import mainapp.tools.photo_upload as photo_upload
import mainapp.tools.exif as exif


log = logging.getLogger(__name__)


@login_required
def handout_notify_contacts(request):
    if not request.user.is_superuser:
        return HttpResponse("hmmm...")

    # Get handouts ready to notify
    handouts_to_notify = models.Handout.objects.filter(is_published=True, has_notified_contacts=False)

    # Check whether GET request for manual verification
    if request.method != 'POST':
        log.info("Notifying contacts: review. Authorization: %s [%s]" % (request.user.username, request.user.id))
        return render(request, 'mainapp/admin/handout_notify.html', {"handouts": handouts_to_notify})

    # POST goes here -- prepare templates and notify contacts!
    log.info("Notifying contacts: Authorization: %s [%s]" % (request.user.username, request.user.id))

    email_text_template = get_template('mainapp/admin/handout_notify_email.txt')
    email_html_template = get_template('mainapp/admin/handout_notify_email.html')
    sms_template = get_template('mainapp/admin/handout_notify_sms.txt')

    count_contacts = 0
    count_email = 0
    count_sms = 0

    for handout in handouts_to_notify:
        log.info("Notifying handout %s" % handout)

        # Prepare templates
        email_msg_text = email_text_template.render(Context({"handout": handout}))
        email_msg_html = email_html_template.render(Context({"handout": handout, "photos": handout.photos.all().order_by("-id")[:5]}))
        sms_msg = sms_template.render(Context({"handout": handout}))

        # Notify contacts
        for contact in handout.contacts.all():
            log.info("- Notifying contact %s" % contact)
            count_contacts += 1

            # Via email
            if contact.email:
                count_email += 1
                log.info("-- via email to %s" % contact.email)
                tools.sendmail.gmail(contact.email, "Photos online at chrishager.at/p/%s" % handout.hash, email_msg_text, email_msg_html)

            # Via SMS
            if contact.tel:
                count_sms += 1
                log.info("-- via sms to %s" % contact.tel)
                tools.sms.send_sms(contact.tel, sms_msg)

        # Finally, update handout
        handout.has_notified_contacts = True
        handout.date_notified_contacts = datetime.datetime.now()
        handout.save()

    return render(request, 'mainapp/admin/handout_notify.html', {"counts": True,
                                                                 "count_contacts": count_contacts, "count_sms": count_sms, "count_email": count_email})


@login_required
def upload_photo(request):
    if request.method == 'POST':
        form = forms.PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                uploader = tools.photo_upload.PhotoUploader(request.FILES["file"])
                uploader.upload()
            except TypeError as e:
                # Not an image file (most likely)
                log.error(e)
                return HttpResponse("Not an image file")

            exif = uploader.exif

            date_captured = ""
            datetime_captured = exif.get("DateTimeOriginal") or exif.get("CreateDate") or exif.get("DateTime")
            if datetime_captured and " " in datetime_captured:
                date_captured = datetime_captured.split(" ")[0]
                date_captured = date_captured.replace(":", "-")  # some cameras use :

            log.info("- creating photo object")
            photo = models.Photo(
                user=request.user,
                photographer=models.UserProfile.get_or_create(request.user),
                hash=uploader.hash,
                is_original=True,
                local_filename=uploader.fn_photo,
                upload_filename=uploader.fn_upload,
                upload_filename_from=uploader.fn_form,
                upload_filesize=os.path.getsize(uploader.fn_upload_full),
                filesize=os.path.getsize(uploader.fn_photo_full),
                date_captured=date_captured,
                resolution_width=uploader.photo_width,
                resolution_height=uploader.photo_height,
                upload_resolution_width=uploader.upload_width,
                upload_resolution_height=uploader.upload_height,
                exif=json.dumps(exif.values),
                title=exif.get("Title"),
                description_md=exif.get("Description"),
                exif_camera="%s %s" % (exif.get("Make"), exif.get("Model")),
                exif_lens=exif.get("Lens") or exif.get("LensModel") or exif.get("LensInfo"),
                exif_exposuretime=exif.get("ExposureTime"),
                exif_aperture=exif.get("Aperture") or exif.get("FNumber") or exif.get("ApertureValue"),
                exif_iso=exif.get("ISO"),
                exif_focallength=exif.get("FocalLength"),
                exif_flash=exif.get("FlashFired")
            )
            photo.save()
            log.info("- created")

            return render(request, 'mainapp/admin/upload.html', {"photo": photo})

    else:
        form = forms.PhotoUploadForm()

    return render(request, 'mainapp/admin/upload.html',
            {"form": form})


@login_required
def admin_index(request):
    return render(request, 'mainapp/admin/index.html')


@login_required
def admin_build_photo_urls(request):
    """
    Create the final url for each photo, based on whether it's stored locally or externally
    """
    log.info("Admin Action: Updating urls. Authorization: %s [%s]" % (request.user.username, request.user.id))
    for photo in models.Photo.objects.all():
        photo.update_url()
        photo.save()
        log.info("- %s: %s" % (photo, photo.url))
    return HttpResponse("200")


@login_required
def admin_cache_clear(request):
    log.info("Admin Action: Clearing cache. Authorization: %s [%s]" % (request.user.username, request.user.id))
    cache.clear()
    return HttpResponse("200")


@login_required
def admin_tmp(request):
    """ Temporary action: EXIF update for all photos """
    log.info("Admin Action: tmp. Authorization: %s [%s]" % (request.user.username, request.user.id))

    # Build order_ids
    for photo in models.Photo.objects.all():
        photo.order_id = photo.pk
        photo.save()

    return HttpResponse("200")


@login_required
def admin_photo_mover(request):
    # Move photos around
    return render(request, 'mainapp/admin/photo_mover.html')
