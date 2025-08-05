import smtplib
from email.message import EmailMessage

def send_email(to, subject, body, sender, password):
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print("Failed to send email:", e)
        return False