import io
import os
import random
import time
from PIL import Image
from string import ascii_uppercase
from fastapi import UploadFile

from app.utils.custom_exceptions import ImageTooSmallException


def absolute_path_for_image(image_name):
    """Returns an absolute path to the image in the /static/images/users/ dir"""

    workdir = os.path.abspath(os.getcwd())
    return os.path.join(workdir, "app", "static", "images", 'users', image_name)


def generate_random_image_name(file_extension: str = "png"):
    """
    Returns a random url safe string with the given file extension

    Args:
    file_extension (string): The extension of the file eg .png or .jpeg

    Returns:
        str: The url safe string appended with the given file extension
    """

    random_alphanumeric_str = "".join(random.choices(ascii_uppercase, k=7))
    utc_timestamp_str = str(time.time()).replace(".", "")
    random_str = "-".join([random_alphanumeric_str, utc_timestamp_str])

    return f"{random_str}.{file_extension}"


def store_image_file(file: UploadFile, location: str = 'users'):
    """
    Stores an image file in app/static/images/ directory

    Args:
    file (UploadFile) : The file to uploaded
    location (string) : The dir in the /static/images/ directory to store the image
        If the directory does not exist, it will be created

    Returns:
        str: The name of the saved image file
    """

    # Ensure we have a users dir in our static/images/ directory
    workdir = os.path.abspath(os.getcwd())
    save_img_path = os.path.join(workdir, "app", "static", "images", location)
    if not os.path.exists(save_img_path):
        os.makedirs(save_img_path)

    image_name = generate_random_image_name()
    file_location = os.path.join(save_img_path, image_name)
    file_content = file.file.read()

    # Save the image to file system
    try:
        img = Image.open(io.BytesIO(file_content))

        dimension = img.size
        if dimension[0] < 180 and dimension[1] < 180:
            raise ImageTooSmallException

        img.thumbnail(size=(500, 500))
        img.save(file_location)
    except OSError:
        # Backup file save mechanism
        with open(file_location, mode="wb+") as f:
            f.write(file_content)

    return image_name
