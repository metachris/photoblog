import os
import string
import random
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

log = logging.getLogger(__name__)


def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def email(to, subject, text, html=None):
    """
    Super light wrapper for djangos send_email

    `to` can either be a single email string or a list of email strings
    """
    if isinstance(to, str) or isinstance(to, unicode):
        to = [to]

    if html:
        msg = EmailMultiAlternatives(subject, text, settings.EMAIL_FROM_DEFAULT, to)
        msg.attach_alternative(html, "text/html")
        msg.send()
    else:
        send_mail(subject, text, settings.EMAIL_FROM_DEFAULT, to)
