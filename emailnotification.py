import os
import glob
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

class EmailNotification:

    def __init__(
            self,
            server="smtp.gmail.com",
            port=587,
            sender="source@gmail.com",
            password="yourpassword",
            recipients=["target@gmail.com"]):

        # Set configuration properties
        self.server = server
        self.port = port
        self.sender = sender
        self.password = password
        self.recipients = recipients
        self.commaspace = ", "

        # Build enclosing (outer) message
        self.outer = MIMEMultipart()
        self.outer['To'] = self.commaspace.join(recipients)
        self.outer['From'] = sender
        self.outer.preamble = "You will not see this in a MIME-aware mail reader.\n"

    def send(self, subject, imagePath):

        # Update subject line
        self.outer['Subject'] = subject

        # Attach image to message when present
        if imagePath:
            try:
                with open(imagePath, 'rb') as fp:
                    msg = MIMEBase('application', "octet-stream")
                    msg.set_payload(fp.read())
                encoders.encode_base64(msg)
                msg.add_header("Content-Disposition", "attachment", filename=os.path.basename(imagePath))
                self.outer.attach(msg)
            except:
                print("[INFO] unable to open file attachments for email notification...")
                raise

        # Stringify the composed message
        composed = self.outer.as_string()

        # Attempt to send email
        try:
            s = smtplib.SMTP(self.server, self.port)
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(self.sender, self.password)
            s.sendmail(self.sender, self.recipients, composed)
            s.close()
            print("[INFO] email notification sent...")
        except:
            print("[INFO] email notification failed to send...")
            raise

        # Return
        return True