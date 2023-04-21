from decouple import config
from twilio.rest import Client

account_sid = config("TWILIO_ACCOUNT_SID")
auth_token = config("TWILIO_AUTH_TOKEN")
from_phone_number = config("TWILLO_FROM_PHONE_NUMBER")


def add_header_greeting(name: str, msg: str):
    """
    Handles prepending the header and greeting to a string
    """
    sms_header = "Expense Tracker\n\n"
    sms_greeting = f"Hello {name},\n"
    return f"{sms_header}{sms_greeting}{msg}"


# SMS MESSAGES
signup_sms = "Your verification code is <otp>\nExpires in 5 minutes"
login_sms = "Your login code is <otp>\nExpires in 2 minutes"


class SMSMessenger:
    """
    A class to send SMS messages
    """

    __client = Client(account_sid, auth_token)
    __from = from_phone_number

    def __init__(self, receiver_name: str, receiver_number: str):
        self.__receiver_name = receiver_name
        self.__to = receiver_number

    def __send_sms(self, message: str):
        self.__client.messages.create(
            from_=self.__from,
            body=message,
            to=self.__to,
        )

    def send_otp(self, otp: str):
        """
        Sends an OTP sms message to the receiver
        """
        msg = add_header_greeting(
            name=self.__receiver_name,
            msg=f"Your one time verification code is {otp}. It expires in 2 minutes",
        )

        self.__send_sms(message=msg)

    def send_signup_msg(self, otp: str):
        msg = add_header_greeting(
            name=self.__receiver_name, msg=signup_sms.replace("<otp>", otp)
        )
        self.__send_sms(message=msg)
