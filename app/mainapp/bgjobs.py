"""
Background jobs via Threads.
"""
import threading
import logging
import time


log = logging.getLogger(__name__)


class BGRunner(threading.Thread):
    """
    Wrapper class that all background jobs extend. Handles the threading
    and logging and exceptions, and can easily be upgraded to a proper
    task distribution system (eg. Celery) later on.
    """
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        log.info("Starting background job %s" % str(self))

        # Execute and wrap in timer
        try:
            t1 = time.time()
            self.execute()
            t2 = time.time()

            # Log time needed for execution
            td = float(int(t2*10) - int(t1*10))/10
            log.info("- finished in %s seconds" % (td))

        except Exception as e:
            log.exception(e)

    def execute(self):
        """Dummy function; overwritten by task specific classes"""
        pass


class SendMail(BGRunner):
    """
    Send an email in the background. Example usage:

        bgjobs.SendMail("chris@metachris.org", "Photoblog Contact", msg).start()

    """
    def __init__(self, to, subject, message_text, message_html=None):
        BGRunner.__init__(self)
        self.to = to
        self.subject = subject
        self.msg_text = message_text
        self.msg_html = message_html

    def __str__(self):
        return "<BGRunner<SendMail(to=%s,subject=%s,text=%s)>>" % (self.to, self.subject, self.msg_text)

    def execute(self):
        from mainapp.tools.sendmail import gmail
        gmail(self.to, self.subject, self.msg_text, self.msg_html)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    sm = SendMail("chris@metachris.org", "subject", "txt")
    sm.start()
