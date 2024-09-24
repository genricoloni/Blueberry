"""
Module for creating a blurred background image from the cover image data.
"""

import io

from PIL import Image, ImageFilter
#pylint: disable=import-error
from utils import images

#pylint: disable=no-member
def create_blurred_image(image, display, radius=20):
    """
    Creates a blurred background image from the cover image data.

    Args:
        cover_image_data (bytes): Image data as bytes.
        display_dimensions (tuple): Dimensions of the display (width, height).
        blur_radius (int): Radius of the Gaussian blur filter.

    """
    try:
        # Resize, crop, and blur the album image

        base_width, base_height = int(display[0]), int(display[1])
        resized_image = images.resize_and_center_image(image, base_width*2, base_height*2)
        blurred_image = resized_image.filter(ImageFilter.GaussianBlur(radius=radius))

        cover_image = image
        cover_width, cover_height = image.size
        cover_image = image.resize((int(1.2 * cover_width),
                                    int(1.2 * cover_height)), Image.LANCZOS)
        x_position = (blurred_image.width - cover_image.width) // 2
        y_position = (blurred_image.height - cover_image.height) // 2
        blurred_image.paste(cover_image, (x_position, y_position))

        save_image(blurred_image)
        return blurred_image

    except io.UnsupportedOperation as e:
        print(f"Error creating blurred background: {e}")
        return None

def save_image(image):
    """
    Save the image to the specified path.

    Args:
        image (Image): The image to save.
        path (str): The path to save the image to.
    """
    try:
        image.save("ImageCache/finalImage.png")
    except io.UnsupportedOperation as e:
        print(f"Error saving image: {e}")
