import logging
import smtplib
from email.MIMEText import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings


log = logging.getLogger(__name__)


def gmail(to, subject, text, html=None):
    log.debug("Sending Email via Gmail to %s" % to)
    sender = "%s <%s>" % (settings.SENDMAIL_SENDER_NAME, settings.SENDMAIL_GMAIL_USER)

    if html:
        msg = MIMEMultipart("alternative")
    else:
        msg = MIMEMultipart()

    msg['From'] = sender
    msg['To'] = to
    msg['Subject'] = subject

    if html:
        msg.attach(MIMEText(text.encode("utf-8"), "plain", _charset="utf-8"))
        msg.attach(MIMEText(html.encode("utf-8"), "html", _charset="utf-8"))
    else:
        msg.attach(MIMEText(text.encode("utf-8"), _charset="utf-8"))

    # Send email
    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(settings.SENDMAIL_GMAIL_USER, settings.SENDMAIL_GMAIL_PASS)
    mailServer.sendmail(sender, to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()
