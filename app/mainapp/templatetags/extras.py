from django import template
from django.template.defaultfilters import stringfilter

import mainapp.forms

register = template.Library()


@register.filter
def split(val, separator=" "):
    return (v for v in val.split(separator) if v)


@register.filter
@stringfilter
def custom_upper(value):
    return value.upper()


@register.tag
def get_contact_form(parser, token):
    class ContactFormRenderer(template.Node):
        def render(self, context):
            # Get the contact form
            contact_form = mainapp.forms.ContactForm()
            return contact_form.as_p()
    return ContactFormRenderer()

