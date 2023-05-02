from twilio.rest import Client as TwilloClient
from asyncio import to_thread
from dataclasses import dataclass

from app.settings import settings
from app.utils.custom_exceptions import SendSmsError


def get_twillo_client(
    sid: str = settings.twillo_account_sid, token: str = settings.twillo_auth_token
):
    return TwilloClient(username=sid, password=token)


def add_header_greeting(name: str, msg: str):
    """
    Handles prepending the header and greeting to a string
    """
    sms_header = "Expense Tracker OTP\n"
    sms_greeting = f"Hello {name},\n"
    return f"{sms_header}{sms_greeting}{msg}"


# SMS MESSAGES
signup_sms = "Your verification code is <otp>\nExpires in 5 minutes"
login_sms = "Your login code is <otp>\nExpires in 2 minutes"


@dataclass
class SMSMessenger:
    """Handles Sending SMS using Twillo Client"""

    receiver_phone: str
    receiver_name: str = ""

    def __engine(self, msg: str, client: TwilloClient = get_twillo_client()):
        client.messages.create(
            from_=settings.twillo_from_phone_number, body=msg, to=self.receiver_phone
        )

    async def send(self, msg: str):
        try:
            await to_thread(self.__engine, msg)
        except Exception as e:
            raise SendSmsError(str(e))

    async def send_otp(self, otp: str):
        msg = add_header_greeting(
            name=self.receiver_name,
            msg=f"Your one time verification code is {otp}. It expires in 2 minutes",
        )

        await self.send(msg=msg)

    async def send_welcome(self, otp: str):
        msg = add_header_greeting(
            name=self.receiver_name, msg=signup_sms.replace("<otp>", otp)
        )
        await self.send(msg=msg)
