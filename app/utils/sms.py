from twilio.rest import Client
from asyncio import to_thread

from app.settings import settings
from app.models import User as UserOrm


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


class SMSMessenger:
    def __init__(
        self,
        user: UserOrm,
        client: Client,
        sid: str = settings.twillo_account_sid,
        token: str = settings.twillo_auth_token,
    ):
        assert user.phone_number, "The User must have a phone number"
        assert user.first_name, "The User must have a first name"
        assert user.last_name, "The User must have a last name"
        assert client is not None, "Provide a client"

        self.__receiver_name = f"{user.first_name}  {user.last_name}"
        self.__to = user.phone_number
        self.__client = client
        self.__sid = sid
        self.__token = token
        self.__from = settings.twillo_from_phone_number

    def __engine(self, msg: str):
        client = self.__client(self.__sid, self.__token)
        client.messages.create(from_=self.__from, body=msg, to=self.__to)

    async def send(self, msg: str):
        return await to_thread(self.__engine, msg)

    async def send_otp(self, otp: str):
        msg = add_header_greeting(
            name=self.__receiver_name,
            msg=f"Your one time verification code is {otp}. It expires in 2 minutes",
        )

        await self.send(msg)

    async def send_welcome(self, otp: str):
        msg = add_header_greeting(
            name=self.__receiver_name, msg=signup_sms.replace("<otp>", otp)
        )
        await self.send(msg)
