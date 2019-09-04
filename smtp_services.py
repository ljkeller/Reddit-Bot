import smtplib
import config


def init_email():
    smtp = smtplib.SMTP("smtp.gmail.com", 587)
    smtp.starttls()
    smtp.login(config.bot_email, config.password)
    return smtp

def send_email(smtp: smtplib.SMTP, subject, body):
    message = f'Subject: {subject}\n\n{body}'
    smtp.sendmail(config.bot_email, config.personal_email, message)

s = init_email()
send_email(s, "Test_Header", "This is my test subject! How does it look? Sent "
                          "from my Pi")
s.close()
