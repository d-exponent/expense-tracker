from pydantic import BaseModel, EmailStr, constr
from datetime import datetime


from myapp.utils.error_utils import raise_bad_request_http_error
from myapp.utils.app_utils import remove_none_props_from_dict_recursive


"""
USER PASSWORD REGEX REQUIREMENTS
1. Must have at least one Uppercase letter
2. Must have at least one number character
3. Must have at least one symbol
4. Must be at least eight(8) characters long

"""
password_reg = "^(?=(.*[A-Z]){1,})(?=(.*[0-9]){1,})(?=(.*[!@#$%^&*()\-__+.]){1,}).{8,}$"
data_error_default_msg = "Provide a not None value for at least one attribute"


class UserUtils(BaseModel):
    def get_number_of_not_none_attributes(self) -> int:
        new_copy_without_none = remove_none_props_from_dict_recursive(self.dict())
        return len(new_copy_without_none.items())

    def raise_data_error_exception(self, message: str = data_error_default_msg):
        raise_bad_request_http_error(message)

    def validate_data(self):
        pass


class UserLogin(UserUtils, BaseModel):
    id: int | None
    email: EmailStr | None
    phone: str | None
    password: str

    def validate_data(self):
        if self.get_number_of_not_none_attributes() == 1:
            self.raise_data_error_exception()


class UserUpdate(UserUtils, BaseModel):
    first_name: constr(max_length=40, strip_whitespace=True) = None
    middle_name: constr(max_length=40, strip_whitespace=True) = None
    last_name: constr(max_length=40, strip_whitespace=True) = None
    image: str = None

    def validate_data(self):
        if self.get_number_of_not_none_attributes() == 0:
            self.raise_data_error_exception()


class UserBase(UserUpdate):
    first_name: constr(max_length=40, strip_whitespace=True)
    middle_name: constr(max_length=40, strip_whitespace=True) = None
    last_name: constr(max_length=40, strip_whitespace=True)
    image: str = None
    phone: constr(max_length=25, strip_whitespace=True)
    email: EmailStr | None


class UserCreate(UserBase):
    password: constr(regex=password_reg) | bytes = None


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserAllInfo(UserOut):
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    password_modified_at: datetime = None
    password_reset_token: str = None
    password_reset_token_expires_at: datetime = None

    class Config:
        orm_mode = True
