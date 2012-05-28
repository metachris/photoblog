import datetime
import json
from pprint import pprint

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core import exceptions
from django.template.loader import get_template
from django.template import Context, Template

import models
import forms
import tools
import tools.sendmail


def home(request):
    #return HttpResponse("Hello, world. You're at the poll index.")
    # raise Http404
    photos_per_page = 10
    photos = models.Photo.objects.filter(featured=True).order_by("-id")[:photos_per_page]
    return render(request, 'index.html', {'photos': photos, "count": photos_per_page})


def photo(request, photo_slug):
    photo = models.Photo.objects.get(slug=photo_slug)
    tag_slug = request.GET.get("tag")
    set_slug = request.GET.get("set")

    # Get next and previous photo, based on current browsing
    q_next = models.Photo.objects.filter(id__gt=photo.id).order_by("id")
    q_prev = models.Photo.objects.filter(id__lt=photo.id).order_by("-id")
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
    sets = models.Set.objects.all()

    photo_count = models.Photo.objects.all().count()
    sets_count = models.Set.objects.all().count()

    return render(request, 'mainapp/sets.html', {'sets': sets, "photo_count": photo_count, "sets_count": sets_count})


def tag_photos(request, tag_slug):
    """ Show photos with a specific tag """
    tag = models.Tag.objects.get(slug=tag_slug)
    tags = [tag]
    tags += tag.get_descendants()
    photos = models.Photo.objects.filter(tags__in=tags).order_by("-id")[:10]
    if len(photos) == 1:
        return HttpResponseRedirect('/photo/%s' % photos[0].hash)

    return render(request, 'mainapp/tag_photos.html', {'tag': tag, 'photos': photos})


def location_photos(request, location_slug):
    """ Show photos with a specific tag """
    location = models.Location.objects.get(slug=location_slug)
    locations = [location]
    locations  += location.get_descendants()
    photos = models.Photo.objects.filter(location__in=locations).order_by("-id")[:10]
    if len(photos) == 1:
        return HttpResponseRedirect('/photo/%s' % photos[0].hash)

    return render(request, 'mainapp/location_photos.html', {'location': location, 'photos': photos})


def set_photos(request, set_slug):
    """ Show photos in a set """
    set = models.Set.objects.get(slug=set_slug)
    photos = models.Photo.objects.filter(sets=set).order_by("-id")[:10]
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
    photos = models.Photo.objects.filter(id__lt=photo_last.id)
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
    print ret

    return HttpResponse(json.dumps(ret))


def ajax_contact(request):
    print request.POST
    if request.method == 'POST': # If the form has been submitted...
        form = forms.ContactForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            # All validation rules pass
            # send email now (TODO)
            email_template = get_template('mainapp/email/contact.html')
            msg = email_template.render(Context({ "form": form.cleaned_data}))
            tools.sendmail.gmail("chris@metachris.org", "Photoblog Contact", msg)
            return HttpResponse('1')
        else:
            return HttpResponse(str(form.errors))
    else:
        return HttpResponse("wrong turn?")
