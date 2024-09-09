from PIL import Image, ImageDraw
from utils.images import paste_and_save_album_image

def create_album_image(display, image, text, colors):
      """
      Create a png file where the album cover is placed in the center of the screen.
      """

      background = create_color_background(int(display[0]), int(display[1]), colors)
      paste_and_save_album_image(background, image, display, text)

        
def create_color_background(baseWidth, baseHeight, colors):
    """
    Create a background image with two colors.
    
    Args:
        baseWidth (int): The width of the background image.
        baseHeight (int): The height of the background image.
        colors (list): A list of two colors to use for the background.
        
    Returns:
        Image: A new background image with two colors."""
    
    colorImageOne = Image.new('RGB', (baseWidth, int(baseHeight / 2)), colors[0].rgb)
    colorImageTwo = Image.new('RGB', (baseWidth, int(baseHeight / 2)), colors[1].rgb)

    background = Image.new('RGB', (colorImageOne.width, colorImageOne.height + colorImageTwo.height))
    background.paste(colorImageOne, (0, 0))
    background.paste(colorImageTwo, (0, colorImageOne.height))

    return background

