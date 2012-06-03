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
    key = "photo<%s>-alt:" % photo.id

    # See if we can get that cached
    cached = cache.get(key)
    if cached:
        return cached

    ret = "Photo '{photo.title}'"
    if photo.photographer or photo.date_captured or photo.location:
        ret += ", captured"
    if photo.photographer and photo.photographer.name:
        ret += " by {photo.photographer.name}"
    if photo.date_captured:
        if photo.photographer:
            ret += " on %s" % date_filter(photo.date_captured)
    if photo.location:
            ret += " in {photo.location.name}"
    ret = ret.format(photo=photo).replace('"', "'")
    cache.set(key, ret, 60)
    return ret

#@register.tag
#def get_contact_form(parser, token):
#    class ContactFormRenderer(template.Node):
#        def render(self, context):
#            # Get the contact form
#            contact_form = mainapp.forms.ContactForm()
#            return contact_form.as_p()
#    return ContactFormRenderer()

