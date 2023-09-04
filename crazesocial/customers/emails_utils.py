import smtplib
from email.message import EmailMessage
from django.conf import settings

def send_email_notifications(username, receiver_email):
    msg = EmailMessage()
    msg['Subject'] = 'Welcome to CrazeSocial'
    msg['From'] = 'alpha@crazesocial.com'
    msg['To'] = receiver_email
    mail_content = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title></title>
    </head>
    <body>
        <p>Hi, <b>{username}</b></p>

        Welcome to Craze Social. We offer the best social media
        metrics and comparison strategy. Stay tuned, there's more
        to come.
    </body>
    </html>    

    '''

    try:
        msg.set_content(mail_content, subtype='html')
        smtp = smtplib.SMTP('smtp.office365.com', 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD) 
        smtp.send_message(msg)
        smtp.quit()
        print("Email sent successfully...")
    except:
        print("Error While sending email...")