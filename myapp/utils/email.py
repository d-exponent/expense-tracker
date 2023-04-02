import smtplib
from email.message import EmailMessage
from myapp.schema.user import UserOut
from decouple import config

app_email = config("EMAIL_ADDRESS")
app_email_password = config("EMAIL_PASSWORD")


def send_otp_to_new_user_email(user: UserOut):
    msg = EmailMessage()
    msg["Subject"] = "Subject of the Email"  # Subject of Email
    msg["From"] = app_email
    msg["To"] = user.email

    # TODO: ADD CONTENT
    msg.set_content("")

    try:
        with smtplib.SMTP(host="smtp.office365.com", port=587) as connection:
            connection.ehlo()
            connection.starttls()
            connection.login(user=app_email, password=app_email_password)
            connection.sendmail(
                from_addr=app_email, to_addrs="desmondodion24@gmail.com", msg=""
            )
    except Exception:
        pass
