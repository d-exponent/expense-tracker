from fastapi import UploadFile, File, Form
from typing import Annotated
from pydantic import EmailStr

from app.schema.user import UserCreate, password_reg, e_164_phone_regex
from app.utils.file_upload import store_image_file, ImageTooSmallException
from app.utils.error_utils import RaiseHttpException
from app.utils.general import to_title_case


def handle_user_multipart_data_create(
    *,
    profile_image: UploadFile = File(default=None),
    first_name: Annotated[str, Form()],
    middle_name: str = Form(default=None),
    last_name: Annotated[str, Form()],
    email: EmailStr = Form(default=None),
    phone: Annotated[str, Form(regex=e_164_phone_regex)],
    password: str = Form(default=None, regex=password_reg),
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
        first_name=to_title_case(first_name),
        last_name=to_title_case(last_name),
        middle_name=to_title_case(middle_name) if middle_name else None,
        phone=phone,
        email=email.lower() if email else None,
        password=password,
        image_url=image_name,
        role="user",
    )
