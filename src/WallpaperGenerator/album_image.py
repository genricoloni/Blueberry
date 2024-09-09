from PIL import Image, ImageDraw

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

def paste_and_save_album_image(bg, cover, display, text):
    """
       Paste the album image in the center of the background image and save the final image.
       Args:
           bg (Image): The background image.
           cover (Image): The album image.
           display (tuple): The dimensions of the display.
           text (Image): The text image.
    """

    width = int(display[0])
    height = int(display[1])

    # Paste the album image, bigger of 120% of the size, in the center of the gradient image
    bg.paste(cover, ((int(bg.width/2) - int(cover.width / 2)), int((bg.height/2) - int(cover.height / 2))))
    #save the final image

    background = Image.new('RGB', (width, height))
    background.paste(bg, (0, 0))
    background.paste(text, (0, 0), mask = text)

    background.save("ImageCache/finalImage.png")