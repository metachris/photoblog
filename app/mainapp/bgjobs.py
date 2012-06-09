"""
Background jobs via Threads.
"""
import threading
import logging
import time
from django.shortcuts import render

from mainapp.tools import photoflow, email
from mainapp.views.photopager import ThumbnailPager, Filters


log = logging.getLogger(__name__)


class BGTask(threading.Thread):
    """
    Wrapper class that all background jobs extend. Handles the threading
    and logging and exceptions, and can easily be upgraded to a proper
    task distribution system (eg. Celery) later on.
    """
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        log.info("%s started" % str(self))

        # Execute and wrap in timer
        try:
            t1 = time.time()
            self.execute()
            t2 = time.time()

            # Log time needed for execution
            td = float(int(t2*10) - int(t1*10))/10
            log.info("%s finished in %s seconds" % (str(self), td))

        except Exception as e:
            log.error("Exception in %s:" % str(self))
            log.exception(e)

    def execute(self):
        """Dummy. Overwritten by task specific classes"""
        pass


class SendMail(BGTask):
    """
    Send an email in the background. Example usage:

        bgjobs.SendMail("chris@metachris.org", "Photoblog Contact", msg).start()

    """
    def __init__(self, to, subject, message_text, message_html=None):
        BGTask.__init__(self)
        self.to = to
        self.subject = subject
        self.msg_text = message_text
        self.msg_html = message_html

    def __str__(self):
        return "<BGTask: SendMail(to=%s,subject=%s,text=%s)>" % (self.to, self.subject, self.msg_text)

    def execute(self):
        email(self.to, self.subject, self.msg_text, self.msg_html)


class RebuildFlowFrontpage(BGTask):
    """
    After adding a featured image, all the images on the front page move and resize.
    Resizing takes quite a while so we want to do it in the background while the
    previous layout is still cached. This way the first user already gets the pre-rendered
    thumbnails.
    """
    def __str__(self):
        return "<BGTask: RebuildFlowFrontpage()>"

    def execute(self):
        # Create a flow manager
        flow = photoflow.FlowManager()

        # Get the current page from the pager
        pager = ThumbnailPager(Filters(featured_only=True))
        pager.load_page(photos_per_page="all")

        # Get the flow html and render to response
        flow_html = flow.get_html(pager.photos)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    sm = SendMail("chris@metachris.org", "subject", "txt")
    sm.start()
