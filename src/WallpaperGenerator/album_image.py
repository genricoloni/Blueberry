from PIL import Image
from utils.images import paste_and_save_album_image

def create_album_image(display, image, text, colors):
    """
    Create a PNG file where the album cover is placed in the center of the screen.

    This function generates a background using two colors and pastes the album cover image in the center.
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


def create_color_background(baseWidth, baseHeight, colors):
    """
    Create a background image with two distinct colors.

    This function creates a background where the top half is filled with the first color
    and the bottom half is filled with the second color.

    Args:
        baseWidth (int): The width of the background image.
        baseHeight (int): The height of the background image.
        colors (list): A list of two colors to use for the background. Each color should be in an RGB tuple format.

    Returns:
        PIL.Image: A new background image composed of two colors.
    """
    # Create the top half of the background with the first color
    colorImageOne = Image.new('RGB', (baseWidth, int(baseHeight / 2)), colors[0].rgb)
    
    # Create the bottom half of the background with the second color
    colorImageTwo = Image.new('RGB', (baseWidth, int(baseHeight / 2)), colors[1].rgb)

    # Create a blank image with the combined height of both halves
    background = Image.new('RGB', (colorImageOne.width, colorImageOne.height + colorImageTwo.height))
    
    # Paste the two color blocks into the background
    background.paste(colorImageOne, (0, 0))  # Top half
    background.paste(colorImageTwo, (0, colorImageOne.height))  # Bottom half

    return background
