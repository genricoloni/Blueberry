"""
Module for creating album cover images with a background.
"""
from PIL import Image
# pylint: disable=import-error
from utils.images import paste_and_save_album_image

def create_album_image(display, image, text, colors):
    """
    Create a PNG file where the album cover is placed in the center of the screen.

    This function generates a background using two colors and pastes the 
    album cover image in the center.
    The final image is then saved as a PNG file.

    Args:
        display (tuple): A tuple containing the display's width and height (width, height).
        image (PIL.Image): The album cover image to be placed in the center.
        text (str): The text to be displayed along with the image.
        colors (list): A list of two colors used to create the background.
    """
    # Create a color background
    background = create_color_background(int(display[0]), int(display[1]), colors)

    # Paste the album image and save the final image
    paste_and_save_album_image(background, image, display, text)


def create_color_background(base_width, base_height, colors):
    """
    Create a background image with two distinct colors.

    This function creates a background where the top half is filled with the first color
    and the bottom half is filled with the second color.

    Args:
        base_width (int): The width of the background image.
        base_height (int): The height of the background image.
        colors (list): A list of two colors to use for the background. 
            Each color should be in an RGB tuple format.

    Returns:
        PIL.Image: A new background image composed of two colors.
    """
    # Create the top half of the background with the first color
    color_image_ne = Image.new('RGB', (base_width, int(base_height / 2)), colors[0].rgb)

    # Create the bottom half of the background with the second color
    color_image_two = Image.new('RGB', (base_width, int(base_height / 2)), colors[1].rgb)

    # Create a blank image with the combined height of both halves
    background = Image.new('RGB', (color_image_ne.width,
                                   color_image_ne.height + color_image_two.height))

    # Paste the two color blocks into the background
    background.paste(color_image_ne, (0, 0))  # Top half
    background.paste(color_image_two, (0, color_image_ne.height))  # Bottom half

    return background
