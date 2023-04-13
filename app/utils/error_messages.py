class UserNotExist:
    does_not_exist = "The user does not exist."


class InvalidCredentials:
    email_password_required = (
        "Invalid Credentials. Provide the email address and password for the user."
    )
    invalid_password = "Incorrect password"
    invalid_otp = "Invalid OTP. Provide the OTP for the user."
    expired_otp = "Expired OTP. Provide the OTP for the user."


class UserErrorMessages(UserNotExist):
    already_exists = "This user already exists."
    no_users = "There are no users"


class SignupErrorMessages:
    server_error = "Error while signing up the user. Try again!"
    otp_send_error = "Signup succesfull. Login with phone number to get one time password and complete your registration"
    already_exists = "The user already exists"
    provide_credentials = "Provide a valid email address and password"


class GetMobileOtpErrorMessages(UserNotExist):
    otp_send_error = "Error while sending the one time password. Try again!"
    update_user_error = "Error processing this request. Try again!"
