"""Email threading  """
import os
from os.path import basename
import threading
from django.core.mail import EmailMultiAlternatives
from email.mime.application import MIMEApplication


class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list, sender, files):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        self.sender = sender
        self.files = files
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMultiAlternatives(self.subject, self.html_content,
                                     self.sender, self.recipient_list)
        msg.content_subtype = 'html'
        basedir = os.path.realpath(os.path.dirname("HelpDesk"))
        if self.files == " ":
            pass
        else:
            try:
                with open(basedir+self.files, "r") as fil:
                    part = MIMEApplication(
                        fil.read(),
                        Name=basename(self.files)
                    )
            # After the file is closed
                part['Content-Disposition'] = 'attachment; filename="%s"' % basename(self.files)
                msg.attach(part)

            except Exception as exception:
                print(exception)
                msg.attach_file(basedir+self.files)


def send_html_mail(subject, html_content, recipient_list, sender, files):
    EmailThread(subject, html_content, recipient_list, sender, files).start()
