import threading
import smtplib
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Emailer(threading.Thread):
    def __init__(self, file = None, user = None):
        self.file = file
        self.user = user
        threading.Thread.__init__(self)
        with open(r"/home/tme/passwd.txt") as file:
            self.passwd = file.readlines()
        with open(r"/home/tme/email.txt") as file:
            self.email = file.readlines()
        with open(r"/home/tme/receivers.txt") as file:
            self.receivers = file.readlines()

    def run(self):
        msg = MIMEMultipart()
        if self.file != None:
            fp = open(self.file, 'rb')
            img = MIMEImage(fp.read())
            fp.close()
            msg.attach(img)

        if self.user != None:
            msg['Subject'] = self.user + " Has Unlocked Cage Door"
            msg.preamble = 'Someone has unlocked the cage'
        else:
            msg['Subject'] = "The cage door has been opened for 30 minutes"
            msg.preamble = 'Go close the cage door'
        msg['From'] = self.email
        msg['To'] = self.receivers


        try:
            smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.login(self.email, self.passwd)
            smtpObj.send_message(msg)
            smtpObj.quit()
        except smtplib.SMTPDataError:
            print("Message not sent")
