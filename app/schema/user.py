from pydantic import BaseModel, EmailStr, constr
from datetime import datetime

from app.schema.bill_payment import BillOut
from app.utils.app_utils import remove_none_props_from_dict_recursive as rnd
from app.utils.error_utils import RaiseHttpException


"""
USER PASSWORD REGEX REQUIREMENTS
1. Must have at least one Uppercase letter
2. Must have at least one number character
3. Must have at least one symbol
4. Must be at least eight(8) characters long

"""
e_164_fmt_regex = "^\\+[1-9]\\d{1,14}$"
password_reg = (
    "^(?=(.*[A-Z]){1,})(?=(.*[0-9]){1,})(?=(.*[!@#$%^&*()\\-__+.]){1,}).{8,}$"
)


class UserPassword(BaseModel):
    password: constr(regex=password_reg)


class UserBase(BaseModel):
    first_name: constr(max_length=40, strip_whitespace=True)
    middle_name: constr(max_length=40, strip_whitespace=True) = None
    last_name: constr(max_length=40, strip_whitespace=True)
    phone_number: constr(max_length=25, regex=e_164_fmt_regex, strip_whitespace=True)
    email_address: EmailStr | None
    image_url: constr(strip_whitespace=True) = None
    role: str


class UserUpdate(BaseModel):
    first_name: constr(max_length=40, strip_whitespace=True) = None
    middle_name: constr(max_length=40, strip_whitespace=True) = None
    last_name: constr(max_length=40, strip_whitespace=True) = None
    image_url: constr(strip_whitespace=True) = None
    email_address: EmailStr | None
    phone_number: constr(
        max_length=25, regex=e_164_fmt_regex, strip_whitespace=True
    ) = None

    def validate_data(self):
        """
        Ensure that there is at least one valid property to be updated\n
        Ensures Email addres and phone number won't be updated
        """

        if self.email_address:
            RaiseHttpException.bad_request(
                "Email address cannot be updated via this route"
            )

        if self.phone_number:
            RaiseHttpException.bad_request(
                "Phone number cannot be updated via this route"
            )

        # CHECK THAT THERE IS AT LEAST ONE VALUE TO BE UPDATED
        filtered = rnd(self.__dict__)

        if len(filtered.items()) == 0:
            RaiseHttpException.bad_request("Provide at least one value to update")

        return filtered


class UserCreate(UserBase, UserPassword):
    pass


class UserLoginEmailPassword(UserPassword):
    email_address: EmailStr


class UserUpdatePassword(UserPassword):
    new_password: constr(regex=password_reg)
    new_password_confirm: constr(regex=password_reg)


class UserLoginPhoneNumber(BaseModel):
    phone_number: constr(max_length=25, regex=e_164_fmt_regex, strip_whitespace=True)


class UserLoginId(BaseModel):
    id: int | None


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserOutWithBills(UserOut):
    user_bills: list[BillOut] = []


class UserAuthSuccess(BaseModel):
    user: UserOut
    access_token: str
    token_type: str
    message: str


class UserSignUp(UserCreate):
    otp: str = None
    otp_expires_at: datetime = None

    class Config:
        orm_mode = True


# Password must never ever ever ever be sent from our server
class UserAllInfo(UserOut):
    otp: str = None
    otp_expires_at: datetime = None
    is_active: bool = True
    created_at: datetime
    verified: bool
    updated_at: datetime
    password_modified_at: datetime = None
    password_reset_token: str = None
    password_reset_token_expires_at: datetime = None

    class Config:
        orm_mode = True
