class UserNotExist:
    does_not_exist = "The user does not exist."


class InvalidCredentials:
    email_password_required = (
        "Provide the valid email address and password for the user."
    )
    invalid_password = "Incorrect password"
    invalid_otp = "Invalid OTP"
    expired_otp = "Expired OTP"


class UserErrorMessages(UserNotExist):
    already_exists = "This user already exists."
    no_users = "There are no users"


class GetMobileOtpErrorMessages(UserNotExist):
    otp_send_error = "Error while sending the one time password. Try again!"
    update_user_error = "Error processing this request. Try again!"
