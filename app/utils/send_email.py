import ssl
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Any
import asyncio

from app.settings import settings


signup_message = """
            We are glad help you keep track of your bills.

            Please complete your verifiction with this one-time-password

            <otp>

            Expense tracker team.
        """


@dataclass
class EmailMessenger:
    receiver_email: str
    receiver_name: str = ""
    app_email: str = settings.email_address
    message_setter: EmailMessage | Any = EmailMessage()

    def _set_msg(self):
        msg = self.message_setter
        msg["from"] = self.app_email
        msg["to"] = self.receiver_email
        return msg

    def __engine(self, msg):
        with smtplib.SMTP(host="smtp.office365.com", port=587) as con:
            con.ehlo()
            con.starttls(context=ssl.create_default_context())
            con.login(user=self.app_email, password=settings.email_password)
            con.send_message(msg)

    async def send(self, msg):
        return await asyncio.to_thread(self.__engine, msg)

    @property
    def get_greeting(self):
        return "Hello " + self.receiver_name

    async def send_welcome(self, otp):
        subject = f"{self.get_greeting}, Welcome to the Expense Tracker Family!🥳"
        msg = self._set_msg()
        msg["subject"] = subject
        content = signup_message.replace("<otp>", otp)
        msg.set_content(content)
        await self.send(msg)

    async def send_login(self, otp):
        msg = self._set_msg()
        msg["subject"] = f"{self.get_greeting}, Your One Time Login Password!"
        content = f"Your One Time Login Password is {otp}.\n Expires in 3 minutes"
        msg.set_content(content)
        await self.send(msg)
