import threading
import smtplib
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


#The Emailer class inherits from the Thread class so that it can be run in a separate thread and not hold up the main
#process
class Emailer(threading.Thread):
    # self.file is a picture that will be sent inside the message, None if no file is given
    # self.user is the user that triggered the message being sent, None if no user is given
    def __init__(self, file = None, user = None):
        self.file = file
        self.user = user
        threading.Thread.__init__(self)
        #Read the email password from a text file
        with open(r"/home/tme/passwd.txt") as file:
            self.passwd = file.readline()
        #Read the email that will be sending the message
        with open(r"/home/tme/email.txt") as file:
            self.email = file.readline()
        #Read the emails that will be receiving the message
        with open(r"/home/tme/receivers.txt") as file:
            self.receivers = file.readline()

    #The run function is called when the thread starts
    def run(self):
        msg = MIMEMultipart()
        # If file is not None then read the file and attach it to the message
        if self.file != None:
            fp = open(self.file, 'rb')
            img = MIMEImage(fp.read())
            fp.close()
            msg.attach(img)

        # If user is not None set the subject with the users name, else use default time out subject
        if self.user != None:
            msg['Subject'] = self.user + " Has Unlocked Cage Door"
            msg.preamble = 'Someone has unlocked the cage'
        else:
            msg['Subject'] = "The cage door has been opened for 30 minutes"
            msg.preamble = 'Go close the cage door'
        # Set from to self.email and set to the to recipients
        msg['From'] = self.email
        msg['To'] = self.receivers

        # Try sending the email, if error occurs print that the message was not sent
        try:
            smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.login(self.email, self.passwd)
            smtpObj.send_message(msg)
            smtpObj.quit()
        except smtplib.SMTPDataError:
            print("Message not sent")
