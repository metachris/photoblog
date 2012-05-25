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

    # Get next photo
    q_next = models.Photo.objects.filter(id__gt=photo.id).order_by("id")
    q_prev = models.Photo.objects.filter(id__lt=photo.id).order_by("-id")
    if tag_slug:
        tag = models.Tag.objects.get(slug=tag_slug)
        tags = [tag]
        tags += tag.get_descendants()
        q_next = q_next.filter(tags__in=tags)
        q_prev = q_prev.filter(tags__in=tags)

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


def tags(request):
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
    return render(request, 'mainapp/tags.html', {'tags': tags})


def tag(request, tag_slug):
    """ Show a list of tags """
    tag = models.Tag.objects.get(slug=tag_slug)
    tags = [tag]
    tags += tag.get_descendants()
    photos = models.Photo.objects.filter(tags__in=tags).order_by("-id")[:10]
    if len(photos) == 1:
        return HttpResponseRedirect('/photo/%s' % photos[0].hash)

    return render(request, 'mainapp/tag_photos.html', {'tag': tag, 'photos': photos})


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
    if set_slug: photos = photos.filter(set__slug=set_slug)
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
