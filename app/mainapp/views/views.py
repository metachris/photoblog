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
from django.core import exceptions
from django.template.loader import get_template
from django.template import Context, Template
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required

from django.conf import settings

import mainapp.models as models
import mainapp.forms as forms
import mainapp.tools as tools
import mainapp.tools.sendmail as sendmail
import mainapp.tools.mailchimp as mailchimp
from mainapp.views.photopager import *
from mainapp.tools import photoflow
from mainapp import adminvalues

log = logging.getLogger(__name__)


@cache_page(60 * 15)
def home(request):
#    page = ThumbnailPager(Filters(featured_only=True)).load_page()
#    return render(request, 'index.html', {'page': page})
    # Create a flow manager
    flow = photoflow.FlowManager()

    # Calculate the number of photos for the initial blocks
    blocks_initial = adminvalues.get_int(adminvalues.PHOTOFLOW_BLOCKS_INITIAL)
    photo_count = sum(flow.get_items_per_block(n) for n in xrange(blocks_initial))

    # Get the photos for the current page
    pager = ThumbnailPager(Filters(featured_only=True))
    pager.load_page(photos_per_page=photo_count)

    # Build the flow-html and render to response
    flow_html = flow.get_html(pager.photos)
    return render(request, 'index.html', {'page': pager, "flow_html": flow_html })


@cache_page(60 * 15)
def sitemap(request):
    sets = models.Set.objects.filter(published=True).order_by("-id")
    tags = models.Tag.objects.all().order_by("-id")
    locations = models.Location .objects.all().order_by("-id")
    photos = models.Photo.objects.filter(published=True).order_by("-id")
    return render(request, 'sitemap.xml', {'photos': photos, "sets": sets, "locations": locations, "tags": tags})


@cache_page(60 * 15)
def photo(request, photo_slug):
    photo = models.Photo.objects.get(slug=photo_slug)
    tag_slug = request.GET.get("tag")
    set_slug = request.GET.get("set")
    location_slug = request.GET.get("location")

    # Get next and previous photo, based on current browsing
    q_next = models.Photo.objects.filter(order_id__gt=photo.order_id, published=True).order_by("order_id")
    q_prev = models.Photo.objects.filter(order_id__lt=photo.order_id, published=True).order_by("-order_id")
    linkvars = ""
    if tag_slug:
        tag = models.Tag.objects.get(slug=tag_slug)
        tags = [tag]
        tags += tag.get_descendants()
        q_next = q_next.filter(tags__in=tags)
        q_prev = q_prev.filter(tags__in=tags)
        linkvars = "tag=%s" % tag_slug
    elif location_slug:
        location = models.Location.objects.get(slug=location_slug)
        locations = [location]
        locations += location.get_descendants()
        q_next = q_next.filter(location__in=locations)
        q_prev = q_prev.filter(location__in=locations)
        linkvars = "location=%s" % location_slug
    elif set_slug:
        cur_set = models.Set.objects.get(slug=set_slug)
        q_next = q_next.filter(sets=cur_set)
        q_prev = q_prev.filter(sets=cur_set)
        linkvars = "set=%s" % set_slug

    next = q_next[0] if q_next.count() else None
    prev = q_prev[0] if q_prev.count() else None
    return render(request, 'mainapp/photo.html', {'photo': photo, "linkvars": linkvars, "next": next, "prev": prev})


#def register(request):
#    if request.method == 'POST':
#        form = forms.RegisterForm(request.POST)
#
#        if form.is_valid():
#            user = User.objects.create_user(
#                form.cleaned_data["username"],
#                form.cleaned_data["email"],
#                form.cleaned_data["password"])
#            models.UserProfile.objects.create(user=user)
#            user_authenticated = auth.authenticate(
#                username=form.cleaned_data["username"],
#                password=form.cleaned_data["password"])
#            auth.login(request, user_authenticated)
#            return HttpResponseRedirect('/')
#    else:
#        form = forms.RegisterForm()
#
#    return render(request, 'register.html', {'form': form})
#

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")


@cache_page(60 * 15)
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


@cache_page(60 * 15)
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


@cache_page(60 * 15)
def sets_list(request):
    """ Show a sets of tags """
    sets = models.Set.objects.filter(published=True)
    photo_count = models.Photo.objects.all().count()
    sets_count = models.Set.objects.all().count()
    return render(request, 'mainapp/sets.html', {'sets': sets, "photo_count": photo_count, "sets_count": sets_count})


@cache_page(60 * 15)
def tag_photos(request, tag_slug):
    """ Show photos with a specific tag """
    tag = models.Tag.objects.get(slug=tag_slug)
    page = ThumbnailPager(Filters(tags=[tag_slug])).load_page()
    return render(request, 'mainapp/tag_photos.html', {'tag': tag, 'page': page})


@cache_page(60 * 15)
def location_photos(request, location_slug):
    """ Show photos with a specific tag """
    location = models.Location.objects.get(slug=location_slug)
    page = ThumbnailPager(Filters(location=location_slug)).load_page()
    return render(request, 'mainapp/location_photos.html', {'location': location, 'page': page})


@cache_page(60 * 15)
def set_photos(request, set_slug):
    """ Show photos in a set """
    set = models.Set.objects.get(slug=set_slug)
    page = ThumbnailPager(Filters(sets=[set_slug])).load_page()
    return render(request, 'mainapp/set_photos.html', {'set': set, 'page': page})


@cache_page(60 * 15)
def ajax_photo_more(request):
    is_flow_mode = request.REQUEST.get("type") == "flow"
    if is_flow_mode:
        blocks_initial = adminvalues.get_int(adminvalues.PHOTOFLOW_BLOCKS_INITIAL)
        blocks_perpage = adminvalues.get_int(adminvalues.PHOTOFLOW_BLOCKS_PERPAGE)

        ajax_page_count = int(request.REQUEST.get("page"))  # 0-indexed
        cur_block = blocks_initial + (ajax_page_count * blocks_perpage)  # 0-indexed

        # Count the photos for the currently requested blocks
        flow = photoflow.FlowManager()
        photo_count = sum(flow.get_items_per_block(n) for n in xrange(cur_block, cur_block+blocks_perpage))

        pager = ThumbnailPager.from_request(request)
        pager.load_page(photos_per_page=photo_count)
        ret = {
            "html": flow.get_html(pager.photos, block_offset=cur_block),
            "has_more": pager.has_more,
            "last_hash": pager.last_hash,
        }

    else:
        n = adminvalues.get_int(adminvalues.PHOTOGRID_ITEMS_PERPAGE)
        pager = ThumbnailPager.from_request(request)
        pager.load_page(photos_per_page=n)

        ret = {
            "photos": [],
            "has_more": pager.has_more,
            "last_hash": pager.last_hash,
        }

        griditem_template = get_template('mainapp/photogrid_item.html')
        for photo in pager.photos:
            ret["photos"].append(griditem_template.render(Context({ "photo": photo })))

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
            sendmail.gmail("chris@metachris.org", "Photoblog Contact", msg)

            # If requested, subscribe to newsletter
            if request.POST.get("add_to_list") != "false":
                email = form.cleaned_data["email"]
                mailchimp.mailchimp_subscribe(email)

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

        # Sanitize phone number
        phone = phone.strip().replace(" ", "").replace("-", "").replace("/", "")

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
        sendmail.gmail("chris@metachris.org", "Photoblog Handout Contact", msg)

        # If requested, subscribe to newsletter
        if add_to_list and email:
            mailchimp.mailchimp_subscribe(email)

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
def view_flow(request):
    """Show initial flow page"""
    # Allow overwriting layout-ids for testing with eg. '/flow/?l=0,3'
    _layout_ids = request.GET.get("l")
    layout_ids = [int(id) for id in _layout_ids.split(",")] if _layout_ids else None

    # Create a flow manager
    flow = photoflow.FlowManager(layout_ids=layout_ids, is_test_layouts=True)

    # Calculate the number of photos for the initial blocks
    photo_count = sum(flow.get_items_per_block(n) for n in xrange(adminvalues.get_int(adminvalues.PHOTOFLOW_BLOCKS_INITIAL)))

    # Get the current page from the pager
    pager = ThumbnailPager(Filters(featured_only=True))
    pager.load_page(photos_per_page=photo_count)

    # Get the flow html and render to response
    flow_html = flow.get_html(pager.photos)
    return render(request, 'mainapp/flow.html', {'page': pager, "flow_html": flow_html })
