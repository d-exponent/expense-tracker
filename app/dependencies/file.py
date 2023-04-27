from fastapi import UploadFile, File, Form
import os


from app.utils.files_upload import store_image_file
from app.schema.user import e_164_fmt_regex, password_reg
from pydantic import EmailStr
from app.schema.user import UserCreate
from app.utils.error_utils import RaiseHttpException
from app.utils.custom_exceptions import ImageTooSmallException


def handle_image_save(
    first_name: str = Form(),
    last_name: str = Form(),
    role: str = Form(),
    phone: str = Form(regex=e_164_fmt_regex),
    profile_image: UploadFile = File(default=None),
    middle_name: str = Form(default=None),
    email: EmailStr = Form(default=None),
    password: str = Form(regex=password_reg, default=None),
):
    image_name = ""
    if profile_image:
        # Profile image file can only be an image type
        if not profile_image.content_type.startswith("image/"):
            RaiseHttpException.bad_request(
                "Mimetpe Error! profile_image must be of type image"
            )

        work_dir = os.path.abspath(os.getcwd())
        user_img_dir = os.path.join(work_dir, "app", "static", "images", "users")
        try:
            image_name = store_image_file(file=profile_image, location=user_img_dir)
        except ImageTooSmallException:
            RaiseHttpException.bad_request(
                "The image must be at least 180 X 180 pixels"
            )

    user_create_data = UserCreate(
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        role=role,
        password=password,
        phone_number=phone,
        email_address=email,
        image_url=image_name,
    )

    return user_create_data
