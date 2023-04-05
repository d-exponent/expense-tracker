from decouple import config
from twilio.rest import Client

account_sid = config("TWILIO_ACCOUNT_SID")
auth_token = config("TWILIO_AUTH_TOKEN")
from_phone_number = config("TWILLO_FROM_PHONE_NUMBER")


def add_header_greeting(name: str, msg: str):
    sms_header = "Expense Tracker\n\n"
    sms_greeting = f"Hello {name},\n"
    return f"{sms_header}{sms_greeting}{msg}"


# SMS MESSAGES
signup_sms = "Your verification code is <otp>\nExpires in 5 minutes"
login_sms = "Your login code is <otp>\nExpires in 2 minutes"


class SMSMessenger:
    __client = Client(account_sid, auth_token)
    __from = from_phone_number

    def __init__(self, receiver_name: str, receiver_number: str):
        self.__receiver_name = receiver_name
        self.__to = receiver_number

    def send_sms(self, message: str):
        self.__client.messages.create(
            from_=self.__from,
            body=message,
            to=self.__to,
        )

    def send_signup_otp_sms(self, otp: str):
        signup_msg = signup_sms.replace("<otp>", otp)
        sms_message = add_header_greeting(name=self.__receiver_name, msg=signup_msg)
        self.send_sms(message=sms_message)

    def send_login_otp_sms(self, otp: str):
        login_msg = login_sms.replace("<otp>", otp)
        sms_message = add_header_greeting(name=self.__receiver_name, msg=login_msg)
        self.send_sms(message=sms_message)
