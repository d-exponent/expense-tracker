import ssl
import smtplib
from email.message import EmailMessage
import asyncio

from app.settings import settings


signup_message = """
            We are glad to have you signed up.
            Please complete your verifiction with this one-time-password

            <otp>

            Expense tracker team.
        """


class EmailMessenger:
    __app_email = settings.email_address

    def __init__(self, user, email_msg: EmailMessage):
        assert user.email_address, "The User must have an email address"
        assert user.first_name, "The user must have a first name"
        assert user.last_name, "The user must have a last name"

        self.__user = user
        self.__user_names = self.__user.first_name + " " + self.__user.last_name
        self.__email_msg = email_msg
        self.__greeting = f"Hello {self.__user_names}"

    def __set_msg(self):
        msg = self.__email_msg()
        msg["from"] = self.__app_email
        msg["to"] = self.__user.email_address  # Default subject
        return msg

    def __engine(self, msg):
        with smtplib.SMTP(host="smtp.office365.com", port=587) as con:
            con.ehlo()
            con.starttls(context=ssl.create_default_context())
            con.login(user=self.__app_email, password=settings.email_password)
            con.send_message(msg)

    async def send(self, msg):
        return await asyncio.to_thread(self.__engine, msg)

    async def send_welcome(self, otp):
        msg = self.__set_msg()
        msg["subject"] = f"{self.__greeting}, Welcome to the Expense Tracker Family!🥳"
        content = signup_message.replace("<otp>", otp)
        msg.set_content(content)
        await self.send(msg)

    async def send_login(self, otp):
        msg = self.__set_msg()
        msg["subject"] = f"{self.__greeting}, Your One Time Login Password!"
        content = f"Your One Time Login Password is {otp}.\n Expires in 3 minutes"
        msg.set_content(content)
        await self.send(msg)
