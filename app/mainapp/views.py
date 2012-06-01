import os
import datetime
import json
from pprint import pprint
import logging
import urllib

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core import exceptions
from django.template.loader import get_template
from django.template import Context, Template
from django.core.cache import cache

from django.conf import settings

import models
import forms
import tools
import tools.sendmail
import tools.mailchimp
import tools.sms
import tools.photo_upload
import tools.exif


log = logging.getLogger(__name__)


def home(request):
    #return HttpResponse("Hello, world. You're at the poll index.")
    # raise Http404
    photos_per_page = 10
    photos = models.Photo.objects.filter(published=True, featured=True).order_by("-id")[:photos_per_page]
    return render(request, 'index.html', {'photos': photos, "count": photos_per_page})


def sitemap(request):
    sets = models.Set.objects.filter(published=True).order_by("-id")
    tags = models.Tag.objects.all().order_by("-id")
    locations = models.Location .objects.all().order_by("-id")
    photos = models.Photo.objects.filter(published=True).order_by("-id")
    return render(request, 'sitemap.xml', {'photos': photos, "sets": sets, "locations": locations, "tags": tags})


def photo(request, photo_slug):
    photo = models.Photo.objects.get(slug=photo_slug)
    tag_slug = request.GET.get("tag")
    set_slug = request.GET.get("set")

    # Get next and previous photo, based on current browsing
    q_next = models.Photo.objects.filter(id__gt=photo.id, published=True).order_by("id")
    q_prev = models.Photo.objects.filter(id__lt=photo.id, published=True).order_by("-id")
    if tag_slug:
        tag = models.Tag.objects.get(slug=tag_slug)
        tags = [tag]
        tags += tag.get_descendants()
        q_next = q_next.filter(tags__in=tags)
        q_prev = q_prev.filter(tags__in=tags)
    elif set_slug:
        cur_set = models.Set.objects.get(slug=set_slug)
        q_next = q_next.filter(sets=cur_set)
        q_prev = q_prev.filter(sets=cur_set)

    next = q_next[0] if q_next.count() else None
    prev = q_prev[0] if q_prev.count() else None
    return render(request, 'mainapp/photo.html', {'photo': photo, "tag": tag_slug, "set": set_slug, "next": next, "prev": prev})


def register(request):
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                form.cleaned_data["username"],
                form.cleaned_data["email"],
                form.cleaned_data["password"])
            models.UserProfile.objects.create(user=user)
            user_authenticated = auth.authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"])
            auth.login(request, user_authenticated)
            return HttpResponseRedirect('/')
    else:
        form = forms.RegisterForm()

    return render(request, 'register.html', {'form': form})


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")


def tags_list(request):
    """ Show a list of tags """
    class CountAwareTagTree(object):
        """ Tree based on one root node with model counts """
        tag = None
        model_count = 0
        children = []

        callback = None
        rootlist = None

        def __init__(self, tag, callback=None, rootlist=[]):
            self.tag = tag
            self.callback = callback

            self.count()


            self.rootlist = rootlist or []
            self.rootlist.append(self)

            # Build children tags
            for tag in self.tag.get_children():
                awareTag = CountAwareTagTree(tag, callback=self._signal_count, rootlist=self.rootlist)

        def count(self):
            count = models.Photo.objects.filter(tags__in=[self.tag]).count()
            self._signal_count(count)

        def _signal_count(self, v):
            """Pass the model-count increase through all parents"""
            self.model_count += v
            if self.callback:
                self.callback(v)

    tags = []
    root_tags = models.Tag.get_root_nodes()
    for tag in root_tags:
        tags.append(CountAwareTagTree(tag))

    photo_count = models.Photo.objects.all().count()
    tag_count = models.Tag.objects.all().count()

    return render(request, 'mainapp/tags.html', {'tags': tags, "photo_count": photo_count, "tag_count": tag_count})


def locations_list(request):
    """ Show a list of locations """
    class CountAwareLocationTree(object):
        """ Tree based on one root node with model counts """
        location = None
        model_count = 0
        children = []

        callback = None
        rootlist = None

        def __init__(self, location, callback=None, rootlist=[]):
            self.location = location
            self.callback = callback

            self.count()

            self.rootlist = rootlist or []
            self.rootlist.append(self)

            # Build children tags
            for location in self.location.get_children():
                awareTag = CountAwareLocationTree(location, callback=self._signal_count, rootlist=self.rootlist)

        def count(self):
            count = models.Photo.objects.filter(location=self.location).count()
            self._signal_count(count)

        def _signal_count(self, v):
            """Pass the model-count increase through all parents"""
            self.model_count += v
            if self.callback:
                self.callback(v)

    locations = []
    root_locations = models.Location.get_root_nodes()
    for location in root_locations:
        tree = CountAwareLocationTree(location)
        locations.append(tree)

    photo_count = models.Photo.objects.all().count()
    location_count = models.Location.objects.all().count()

    return render(request, 'mainapp/locations.html', {'locations': locations, "photo_count": photo_count, "location_count": location_count})


def sets_list(request):
    """ Show a sets of tags """
    sets = models.Set.objects.filter(published=True)

    photo_count = models.Photo.objects.all().count()
    sets_count = models.Set.objects.all().count()

    return render(request, 'mainapp/sets.html', {'sets': sets, "photo_count": photo_count, "sets_count": sets_count})


def tag_photos(request, tag_slug):
    """ Show photos with a specific tag """
    tag = models.Tag.objects.get(slug=tag_slug)
    tags = [tag]
    tags += tag.get_descendants()
    photos = models.Photo.objects.filter(tags__in=tags, published=True).order_by("-id")[:10]
#    if len(photos) == 1:
#        return HttpResponseRedirect('/photo/%s' % photos[0].slug)

    return render(request, 'mainapp/tag_photos.html', {'tag': tag, 'photos': photos})


def location_photos(request, location_slug):
    """ Show photos with a specific tag """
    location = models.Location.objects.get(slug=location_slug)
    locations = [location]
    locations  += location.get_descendants()
    photos = models.Photo.objects.filter(location__in=locations, published=True).order_by("-id")[:10]
#    if len(photos) == 1:
#        return HttpResponseRedirect('/photo/%s' % photos[0].hash)

    return render(request, 'mainapp/location_photos.html', {'location': location, 'photos': photos})


def set_photos(request, set_slug):
    """ Show photos in a set """
    set = models.Set.objects.get(slug=set_slug)
    photos = models.Photo.objects.filter(sets=set, published=True).order_by("-id")[:10]
    if len(photos) == 1:
        return HttpResponseRedirect('/photo/%s' % photos[0].hash)

    return render(request, 'mainapp/set_photos.html', {'set': set, 'photos': photos})


def ajax_photo_more(request):
    last_hash = request.GET.get("last")
    photos_per_page = int(request.GET.get("n"))
    featured = request.GET.get("featured")
    tag_slug = request.GET.get("tag")
    set_slug = request.GET.get("set")

    photo_last = models.Photo.objects.get(hash=last_hash)
    photos = models.Photo.objects.filter(id__lt=photo_last.id, published=True)
    if featured: photos = photos.filter(featured=True)
    if tag_slug: photos = photos.filter(tags__slug=tag_slug)
    if set_slug: photos = photos.filter(sets__slug=set_slug)
    photos = photos.order_by("-id")

    ret = {
        "photos": [],
        "has_more": photos.count() - photos_per_page > 0
    }

    griditem_template = get_template('mainapp/photogrid_renderitem.html')
    for photo in photos[:photos_per_page]:
        ret["photos"].append(griditem_template.render(Context({ "photo": photo })));

    ret["last"] = photo.hash
    #print ret

    return HttpResponse(json.dumps(ret))


def ajax_contact(request):
    if request.method == 'POST':
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            # All validation rules pass
            photo = None
            photo_ref = request.POST.get("photo_ref")
            if photo_ref:
                photo = models.Photo.objects.get(hash=photo_ref)

            # Send email
            email_template = get_template('mainapp/email/contact.html')
            msg = email_template.render(Context({
                    "form": form.cleaned_data,
                    "photo": photo
            }))
            tools.sendmail.gmail("chris@metachris.org", "Photoblog Contact", msg)

            # If requested, subscribe to newsletter
            if request.POST.get("add_to_list") != "false":
                email = form.cleaned_data["email"]
                tools.mailchimp.mailchimp_subscribe(email)

            # Return success
            return HttpResponse('1')
        else:
            return HttpResponse(str(form.errors))
    else:
        return HttpResponse("wrong turn?")


def get_handout(request, handout_hash=None):
    """Handout URL"""
    if not handout_hash:
        return render(request, 'mainapp/handout_search.html')

    SESSION_KEY_HAS_SUBSCRIBED = "has_subscribed_to_handout_%s" % handout_hash
    contact_subscribed = request.session.get(SESSION_KEY_HAS_SUBSCRIBED)

    # Users can force-remove the info that they already have subscribed
    if request.GET.get("n") == "1":
        contact_subscribed = request.session[SESSION_KEY_HAS_SUBSCRIBED] = None
        log.debug("Handout: Force-removed session key %s" % SESSION_KEY_HAS_SUBSCRIBED)

    # Handle new subscription
    if request.method == 'POST':
        # Extract data
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        msg = request.POST.get("message")
        add_to_list = request.POST.get("add_to_list") == "on"  # boolean: True or False

        # Poor mans validation
        if not name or (not email and not phone) or (email and (not "." in email or not "@" in email)):
            return render(request, 'mainapp/handout_notyetonline.html', {"id": handout_hash,
                    "error": "Please add your name and email/phone.", "name": name, "email": email,
                    "phone": phone, "msg": msg, "add_to_list": add_to_list
            })
        log.debug("Handout: contact validation passed (%s)" % name)

        # Create Handout Contact
        handout_contact = models.HandoutContact(
            name=name, email=email, tel=phone, subscribed_to_mail_list=add_to_list, hash=models.Handout._mk_hash()
        )
        handout_contact.save()

        # Create Handout if not exists, else add contact
        try:
            handout = models.Handout.objects.get(hash=handout_hash)
        except exceptions.ObjectDoesNotExist:
            handout = models.Handout(hash=handout_hash)
            handout.save()
        handout.contacts.add(handout_contact)

        # All done. Now save the contact to session, send email, etc.
        log.debug("Handout: added contact %s to handout %s" % (handout_contact, handout))
        contact_subscribed = request.session[SESSION_KEY_HAS_SUBSCRIBED] = handout_contact

        # Send email
        email_template = get_template('mainapp/email/contact_handout.html')
        msg = email_template.render(Context({
            "id": handout_hash, "name": name, "email": email, "phone": phone,
            "msg": msg, "add_to_list": add_to_list
        }))
        tools.sendmail.gmail("chris@metachris.org", "Photoblog Handout Contact", msg)

        # If requested, subscribe to newsletter
        if add_to_list and email:
            tools.mailchimp.mailchimp_subscribe(email)

    # See if the handout is already  published
    try:
        handout = models.Handout.objects.get(hash=handout_hash, is_published=True)
        handout.views += 1
        handout.save()
        return render(request, 'mainapp/handout.html', {"id": handout_hash,
                "contact": contact_subscribed, "handout": handout})

    except exceptions.ObjectDoesNotExist:
        return render(request, 'mainapp/handout_notyetonline.html', {"id": handout_hash, "contact": contact_subscribed})


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
                    exif_flash=str(exif.get("FlashFired")) if exif.get("FlashFired") is not None else None,
            )
            photo.save()
            log.info("- created")

            return render(request, 'mainapp/admin/upload.html', {"photo": photo})

    else:
        form = forms.PhotoUploadForm()

    return render(request, 'mainapp/admin/upload.html',
        {"form": form})


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
    dir_upload = os.path.join(settings.MEDIA_ROOT, settings.MEDIA_DIR_UPLOAD)
    dir_photos = os.path.join(settings.MEDIA_ROOT, settings.MEDIA_DIR_PHOTOS)

    for photo in models.Photo.objects.all():
        if not photo.local_filename:
            continue

        try:
            # Compute filenames
            fn_upload = os.path.join(dir_upload, photo.local_filename)
            fn_photos = os.path.join(dir_photos, photo.local_filename)
            log.info("%s | %s" % (photo, photo.local_filename))

            # Add copyright exif tag to original
            os.system("""exiftool "-EXIF:Copyright=%s" %s""" % (settings.EXIF_COPYRIGHT_TAG, fn_upload))

            # Copy exif tags onto resized image
            os.system("""exiftool -tagsFromFile %s %s""" % (fn_upload, fn_photos))

            # Add exif tags to photo and save photo
            exif = tools.exif.ExifToolHolder(fn_upload)
            photo.exif = json.dumps(exif.values)
            photo.exif_camera = "%s %s" % (exif.get("Make"), exif.get("Model"))
            photo.exif_lens = exif.get("Lens") or exif.get("LensModel") or exif.get("LensInfo")
            photo.exif_exposuretime = exif.get("ExposureTime")
            photo.exif_aperture = exif.get("Aperture") or exif.get("FNumber") or exif.get("ApertureValue")
            photo.exif_iso = exif.get("ISO")
            photo.exif_focallength = exif.get("FocalLength")
            photo.exif_flash = str(exif.get("FlashFired")) if exif.get("FlashFired") is not None else None
            photo.save()

        except Exception as e:
            log.warn("- %s" % e)

    return HttpResponse("200")


