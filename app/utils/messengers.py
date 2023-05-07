def replace_otp(words: str, otp: str | int):
    return words.replace("<otp>", otp)


# FOR SMS MESSENGER
signup_sms = "Your verification code is <otp>\nExpires in 10 minutes"

send_otp_sms = "Your one time verification code is <otp>. It expires in 5 minutes"


def add_header_greeting(name: str, msg: str):
    """
    Handles prepending the header and greeting to a string
    """
    sms_header = "Expense Tracker OTP\n"
    sms_greeting = f"Hello {name},\n"
    return f"{sms_header}{sms_greeting}{msg}"


# FOR EMAIL MESSENGER
def add_signature(msg: str):
    return msg + "\nExpense Tracker Team."


def create_content(words: str, otp: str | int):
    return add_signature(replace_otp(words, otp))


signup_message = """
            We are glad help you keep track of your bills.

            Complete your verification with this access code

            <otp>
            It EXPIRES in 10 minutes
        """


login_message = """
                Your One Time Login access code is <otp>.

                Expires in 5 minutes
                """

update_email_message = """
            Use this access code to update your email address <otp>

            Expires in 5 minutes
            """
