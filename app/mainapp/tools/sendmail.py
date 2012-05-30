import logging
import smtplib
from email.MIMEText import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings


log = logging.getLogger(__name__)


def gmail(to, subject, text):
    log.debug("Sending Email via Gmail to %s" % to)
    msg = MIMEMultipart()

    sender = "%s <%s>" % (settings.SENDMAIL_SENDER_NAME, settings.SENDMAIL_GMAIL_USER)
    msg['From'] = sender
    msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(settings.SENDMAIL_GMAIL_USER, settings.SENDMAIL_GMAIL_PASS)
    mailServer.sendmail(sender, to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()
