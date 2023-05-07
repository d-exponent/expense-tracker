import ssl
import asyncio
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

from app.settings import settings
from app.utils import messengers as m
from app.utils.custom_exceptions import SendEmailError


@dataclass
class EmailMessenger:
    """Handles sending email messages"""

    receiver_email: str
    receiver_name: str = ""
    app_email: str = settings.email_address

    def _set_msg(self):
        """Sets the from and to feilds of the message object"""
        msg = EmailMessage()
        msg["From"] = self.app_email
        msg["To"] = self.receiver_email
        return msg

    def _engine(self, msg):
        """Sends email to receiver"""
        try:
            with smtplib.SMTP(host="smtp.office365.com", port=587) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(user=self.app_email, password=settings.email_password)
                server.send_message(msg)

        except Exception as e:
            raise SendEmailError(str(e))

    async def _send(self, msg):
        """Runs _engine in async mode"""
        return await asyncio.to_thread(self._engine, msg)

    @property
    def greeting(self):
        """Returns a greeting"""
        return "Hello " + self.receiver_name

    async def send_welcome(self, otp: str):
        """sends a welcome email with access code (otp) to the reciver

        Args:
            otp (str): The one time password to be embedded in email message
        """

        msg = self._set_msg()
        msg["Subject"] = f"{self.greeting}, Welcome to the Expense Tracker Family!🥳"
        msg.set_content(m.create_content(words=m.signup_message, otp=otp))
        await self._send(msg)

    async def send_login(self, otp):
        """sends login email with access code (otp) to the reciver

        Args:
            otp (str): The one time password to be embedded in email message
        """

        msg = self._set_msg()
        msg["subject"] = f"{self.greeting}, Your One Time Login Password!"
        msg.set_content(m.create_content(m.login_message, otp))
        await self._send(msg)

    async def send_update_email_otp(self, otp):
        """sends an update email with access code (otp) to the reciver

        Args:
            otp (str): The one time password to be embedded in email message
        """

        msg = self._set_msg()
        msg["subject"] = f"{self.greeting}. Your Access Code"
        msg.set_content(m.create_content(m.update_email_message, otp))
        await self._send(msg)
