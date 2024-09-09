import os
from utils.cache import cacheManager
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import colorgram

from WallpaperGenerator.album_image import create_album_image as cai

class WallpaperGenerator:
    """
    A class to manage the generation of wallpapers.

    This class provides methods to generate wallpapers based on album artwork and song details.

    Attributes:
        display (list): The dimensions of the display.
        now_showing (dict): Details of the song currently being displayed.
        cacheManager (cacheManager): The cache manager for managing cached image data.
    """

    def __init__(self):
        """
        Initialize a new instance of the WallpaperGenerator class.

        Fetches the display dimensions and initializes the cache manager.
        """
        self.display = os.popen("xrandr").read().split("\n")[2].split()[0].split("x")
        self.now_showing = None
        self.cacheManager = cacheManager()

    def generate_album_image(self, song_details):
        """
        Generate an album image based on the provided song details.

        If the song is different from the currently displayed song, this method retrieves
        the album artwork, extracts colors, and creates a wallpaper image.

        Parameters:
            song_details (dict): A dictionary containing details of the song (title, artist, image URL).
        """
        if song_details == self.now_showing:
            return

        self.now_showing = song_details
        song_title = song_details['songTitle']
        artist_name = song_details['artistName']
        image_url = song_details['imageUrl']
        colors = self.get_colors(image_url)

        image = self.setup_album_image(self.display, song_details['imageUrl'])
        text = generate_text_image(song_title, artist_name, colors, self.display)

        cai(self.display, image, text, colors)

    def get_colors(self, imageUrl):
        """
        Extract the most common colors from an image.

        Uses the colorgram library to extract the most dominant colors from the image.

        Parameters:
            imageUrl (str): The URL of the image to process.

        Returns:
            list: A list of the two most dominant colors in the image.
        """
        image = Image.open(io.BytesIO(self.cacheManager.get(imageUrl)))

        colors = colorgram.extract(image, 6)

        if len(colors) < 2:
            return [colors[0], colors[0]]

        for i in range(1, len(colors)):
            if colors[i].rgb == colors[0].rgb:
                return [colors[0], colors[i]]
        else:
            return [colors[0], colors[1]]

    def setup_album_image(self, display, imageUrl):
        """
        Create a resized album image for wallpaper.

        This method resizes the album cover to fit the display size and centers it.
        Used in albumImage, controllerImage, and gradient modes.

        Parameters:
            display (list): The dimensions of the display.
            imageUrl (str): The URL of the album image.

        Returns:
            Image: The resized album image to fit the display.
        """
        width = int(int(display[0]) / 5)
        image = Image.open(io.BytesIO(self.cacheManager.get(imageUrl)))

        wpercent = (width / float(image.size[0]))
        hsize = int((float(image.size[1]) * float(wpercent)))

        return image.resize((width, hsize), Image.LANCZOS) 


def generate_text_image(songTitle, artistName, colors, display, positionX=50, positionY=50):
    """
    Generate a text image containing the song title and artist name.

    This function creates an image with the song title and artist name rendered onto it.

    Parameters:
        songTitle (str): The title of the song.
        artistName (str): The name of the artist.
        colors (list): A list of colors to use for the text.
        display (list): The dimensions of the display.
        positionX (int, optional): The x-coordinate of the text. Defaults to 50.
        positionY (int, optional): The y-coordinate of the text. Defaults to 50.

    Returns:
        Image: A new image with the song title and artist name.
    """
    width = int(display[0])
    height = int(display[1])

    textColor = colors[0].rgb

    # Adjust text color to ensure contrast
    if (textColor[0] * 0.299 + textColor[1] * 0.587 + textColor[2] * 0.114) > 186:
        textColor = (0, 0, 0)  # Black text for light backgrounds
    else:
        textColor = (255, 255, 255)  # White text for dark backgrounds

    # Create a new transparent image for the text
    text = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text)

    # Set font and draw the text
    myFont = ImageFont.truetype("./fonts/Rubik.ttf", 40)
    draw.text((positionX, positionY), (songTitle + "\n" + artistName), font=myFont, fill=textColor)

    return text


def calculate_contrast_ratio(color1, color2):
    """
    Calculate the contrast ratio between two colors.

    The contrast ratio is calculated using the formula:
    (L1 + 0.05) / (L2 + 0.05), where L1 and L2 are the relative luminances
    of the two colors.

    Parameters:
        color1 (Color): The first color.
        color2 (Color): The second color.

    Returns:
        float: The contrast ratio between the two colors.
    """
    luminance1 = calculate_relative_luminance(color1)
    luminance2 = calculate_relative_luminance(color2)

    # Ensure luminance1 is the higher value
    if luminance2 > luminance1:
        luminance1, luminance2 = luminance2, luminance1

    return (luminance1 + 0.05) / (luminance2 + 0.05)


def calculate_relative_luminance(color):
    """
    Calculate the relative luminance of a color.

    The luminance is calculated using the formula:
    L = 0.2126 * R + 0.7152 * G + 0.0722 * B

    Parameters:
        color (Color): The color object to calculate luminance for.

    Returns:
        float: The relative luminance of the color.
    """
    r, g, b = color.rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b
