from fastapi import UploadFile, File, Form
from typing import Annotated
from pydantic import EmailStr

from app.schema.user import UserCreate, password_reg, e_164_fmt_regex
from app.utils.file_upload import store_image_file, ImageTooSmallException
from app.utils.error_utils import RaiseHttpException


def handle_user_image_upload(
    *,
    profile_image: UploadFile = File(default=None),
    first_name: Annotated[str, Form()],
    middle_name: str = Form(default=None),
    last_name: Annotated[str, Form()],
    email: EmailStr = Form(default=None),
    phone: Annotated[str, Form(regex=e_164_fmt_regex)],
    password: str = Form(default=None, regex=password_reg),
    role: Annotated[str, Form()],
):
    image_name = None
    if profile_image:
        if not profile_image.content_type.startswith("image"):
            RaiseHttpException.bad_request(
                "Only image files are allowed as profile image"
            )

        try:
            image_name = store_image_file(file=profile_image, location="users")
        except ImageTooSmallException:
            RaiseHttpException.bad_request(
                "The image file is too small. Must be at least 180 X 180 pixels."
            )

    return UserCreate(
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        phone=phone,
        email=email,
        password=password,
        image_url=image_name,
        role=role,
    )
