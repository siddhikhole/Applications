"""Email threading  """
import threading
from django.core.mail import EmailMessage,EmailMultiAlternatives
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from HelpDesk import settings


class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list, sender,files):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        self.sender = sender
        self.files = files
        print("*"*100)
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMultiAlternatives(self.subject, self.html_content, self.sender, self.recipient_list)
        msg.content_subtype = 'html'
        print(self.files)

        if(self.files == " "):
            pass
        else:
            try:
                basedir = os.path.realpath(os.path.dirname("HelpDesk"))
              

                with open(basedir+self.files, "r") as fil:
                    part = MIMEApplication(
                    fil.read(),
                    Name=basename(self.files)
                    )
            # After the file is closed
                part['Content-Disposition'] = 'attachment; filename="%s"' % basename(self.files)
                msg.attach(part)
                print("&"*100)
            except:
                print("_"*100)
                msg.attach_file(basedir+self.files)
        #msg.send()


def send_html_mail(subject, html_content, recipient_list, sender,files):
    print("@"*100)
    EmailThread(subject, html_content, recipient_list, sender,files).start()
