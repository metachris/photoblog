# encoding: utf-8
import datetime
from django import template
from django.template.defaultfilters import stringfilter
from django.template.defaultfilters import date as date_filter
from django.core.cache import cache

import mainapp.forms

register = template.Library()


@register.filter
def split(val, separator=" "):
    return (v for v in val.split(separator) if v)


@register.filter
@stringfilter
def custom_upper(value):
    return value.upper()


@register.filter
def photo_alt(photo):
    key = "photo-alt:%s" % photo.id

    # See if we can get that cached
    cached = cache.get(key)
    if cached:
        return cached

    # Else build, cache and return
    ret = "Photo '{photo.title}'" if photo.title else "Untitled photo"
    if (photo.photographer and photo.photographer.name) or photo.date_captured or photo.location:
        ret += ", captured"
    if photo.photographer and photo.photographer.name:
        ret += " by {photo.photographer.name}"
    if photo.date_captured:
        ret += " on %s" % date_filter(photo.date_captured)
    if photo.location:
        ret += " in {photo.location.name}"
    ret = ret.format(photo=photo).replace('"', "'")
    cache.set(key, ret, 60)
    return ret


@register.filter
def photo_exif_shot(photo):
    """Format photo exif info"""
    ret = u""
    if photo.exif_exposuretime or photo.exif_aperture or photo.exif_iso or photo.exif_focallength:
        if photo.exif_exposuretime:
            if "/" in photo.exif_exposuretime:
                # format for html fraction
                time = photo.exif_exposuretime.split("/")
                ret += "<big><sup>%s</sup>&frasl;<sub>%s</sub> </big>sec" % (time[0], time[1])
            else:
                ret += "{photo.exif_exposuretime} sec"
            if photo.exif_aperture:
                ret += " at "
        if photo.exif_aperture:
            ret += u"ƒ {photo.exif_aperture}"
        if photo.exif_iso:
            if ret:
                ret += ", "
            ret += "ISO {photo.exif_iso}"
        if photo.exif_focallength:
            if ret:
                ret += ", "
            ret += "{photo.exif_focallength}"
        ret = ret.format(photo=photo)
        ret = "<p>%s</p>" % ret
    return ret
