import smtplib
import json

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# creates SMTP session


def send_mail(address_to, token, nick):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()

    with open("C:\\Users\\Modrzew\\PycharmProjects\\ProjectEngineer\\credentials.txt") as file:
        x = file.read()
        credentials = json.loads(x)

        mail_content = '''Hello %s, \nWe're sending you a link. Click it to confirm your email address! \nHere: %s 
        \n \nSafe gardening! \nGarden Warden Team - one guy''' % (nick, credentials['link'] + token)
        # The mail addresses and password
        sender_address = credentials['mail_from']
        sender_pass = credentials['password']
        receiver_address = address_to
        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'Confirm your email address - Garden Warden'  # The subject line
        # The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'plain'))
        # Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
        session.starttls()  # enable security
        session.login(sender_address, sender_pass)  # login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
        print('Mail Sent')
