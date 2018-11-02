import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from base64 import b64decode

def sendingMail():
    sender_addr = "priya.testmailid@gmail.com"
    password = "cHJpeWFAMTIz"
    decoded_pwd = b64decode(password).decode('utf-8')
    receiver_addr = "priya.mishra236@gmail.com"
    
    #mail details
    msg = MIMEMultipart()
    msg['From'] = sender_addr
    msg['To'] = receiver_addr
    msg['Subject'] = "test"
     
    body = "Job not started"
    msg.attach(MIMEText(body, 'plain'))
     
    #login to server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(sender_addr, decoded_pwd)
    
    #sending mail
    text = msg.as_string()
    try:
        server.sendmail(sender_addr,receiver_addr, text)
        return (0)

    except:
        return (1)
    server.quit()
   