import asyncio
from twilio.rest import Client as TwilloClient
from dataclasses import dataclass

from app.settings import settings
from app.utils import messengers as m
from app.utils.custom_exceptions import SendSmsError


twillio_client_config = {
    "username": settings.twillo_account_sid,
    "password": settings.twillo_auth_token,
}


@dataclass
class SMSMessenger:
    """Handles Sending SMS using Twillo Client"""

    receiver_phone: str
    receiver_name: str = ""
    app_phone_num: str = settings.twillo_from_phone_number
    client: TwilloClient = TwilloClient(**twillio_client_config)

    def _engine(self, msg: str):
        self.client.messages.create(
            from_=self.app_phone_num, body=msg, to=self.receiver_phone
        )

    async def _send(self, msg: str):
        try:
            await asyncio.to_thread(self._engine, msg)
        except Exception as e:
            raise SendSmsError(str(e))

    async def send_otp(self, otp: str):
        """Sends generic sms embedded with access code (otp) to the receiver

        Args:
            otp (str): One time password for the reciever
        """
        message = m.replace_otp(m.send_otp_sms, otp)
        msg = m.add_header_greeting(name=self.receiver_name, msg=message)
        await self._send(msg=msg)

    async def send_welcome(self, otp: str):
        """Sends custome signup sms embedded with access code (otp) to the reciver

        Args:
            otp (str): One time password
        """

        message = m.replace_otp(m.signup_sms, otp)
        msg = m.add_header_greeting(name=self.receiver_name, msg=message)
        await self._send(msg=msg)
