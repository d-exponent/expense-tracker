from fastapi import UploadFile, File, Form, Depends
from typing import Annotated
from pydantic import EmailStr

from app.schema.user import UserCreate, password_reg, e_164_phone_regex
from app.utils.file_operations import store_image_file, ImageTooSmallException
from app.utils.error_utils import RaiseHttpException
from app.utils.general import title_case_words


def handle_image_upload(profile_image: UploadFile = File(default=None)):
    image_name = None
    msg = None

    if profile_image is None:
        return image_name

    if profile_image.content_type is None:
        msg = "Oops! You forgot to add an image file to the profile image"
        RaiseHttpException.bad_request(msg)

    if not profile_image.content_type.startswith("image"):
        msg = "Only image files are allowed as a profile image"
        RaiseHttpException.bad_request(msg)

    try:
        image_name = store_image_file(file=profile_image, location="users")
    except ImageTooSmallException:
        msg = "The image file is too small. Image must be at least 180 X 180 pixels."
        RaiseHttpException.bad_request(msg)

    return image_name


def handle_user_multipart_data_create(
    *,
    image_url: Annotated[str, Depends(handle_image_upload)],
    first_name: Annotated[str, Form()],
    middle_name: str = Form(default=None),
    last_name: Annotated[str, Form()],
    email: EmailStr = Form(default=None),
    phone: Annotated[str, Form(regex=e_164_phone_regex)],
    password: str = Form(default=None, regex=password_reg),
    role: str = Form(default='user'),
):
    return UserCreate(
        first_name=title_case_words(first_name),
        last_name=title_case_words(last_name),
        middle_name=title_case_words(middle_name) if middle_name else None,
        phone=phone,
        email=email.lower() if email else None,
        password=password if password else None,
        image_url=image_url,
        role=role,
    )
