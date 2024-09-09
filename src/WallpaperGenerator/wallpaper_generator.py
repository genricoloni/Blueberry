import os
from utils.cache import cacheManager
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import colorgram

from WallpaperGenerator.album_image import create_album_image as cai

class WallpaperGenerator:
    def __init__(self):
        self.display = os.popen("xrandr").read().split("\n")[2].split()[0].split("x")
        self.now_showing = None
        self.cacheManager = cacheManager()

    
    def generate_album_image(self, song_details):
        """
        Generate an album image based on the song details.
        """
        if song_details == self.now_showing:
            return

        print("Generating album image")


        self.now_showing = song_details
        song_title = song_details['songTitle']
        artist_name = song_details['artistName']
        image_url = song_details['imageUrl']
        colors = self.get_colors(image_url)



        image = self.setup_album_image(self.display, song_details['imageUrl'])
        print("DEBUG: setup album image")
        text = generate_text_image(song_title, artist_name, colors, self.display)
        
        print("DEBUG: generated text image")




        album_image = cai(self.display, image, text, colors)
    


    
    def get_colors(self, imageUrl):
        """
        Get the most common colors in the image.
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
        Create a png file where the album cover is palced in the center of the screen.
        This function is used in albumImage, controllerImage and gradient modes.
        """
        width = int(int(display[0]) / 5)
        image = Image.open(io.BytesIO(self.cacheManager.get(imageUrl)))
        print("DEBUG: opened image")
        wpercent = (width / float(image.size[0]))
        hsize = int((float(image.size[1]) * float(wpercent)))
        return image.resize((width,hsize), Image.LANCZOS) 

        
def generate_text_image(songTitle, artistName, colors, display, positionX = 50, positionY = 50):

    print("Generating text image")

    width = int(display[0])
    height = int(display[1])


    textColor = colors[0].rgb

    #if the color is too light, make the text black, otherwise make it white
    if (textColor[0]*0.299 + textColor[1]*0.587 + textColor[2]*0.114) > 186:
        textColor = (int(0), int(0), int(0))
    else:
        textColor = (int(255), int(255), int(255))

    #create a new image with the name of the song and the artist, and transparent background
    text = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    #create a draw object
    draw = ImageDraw.Draw(text)
    #set the font
    myFont = ImageFont.truetype("./fonts/Rubik.ttf", 40)
    #draw the text
    draw.text((positionX,positionY), (songTitle + "\n" + artistName), font = myFont, fill = (textColor[0],textColor[1],textColor[2]))

    #save the text image
    return text



        


def calculate_contrast_ratio(color1, color2):
    # Calculate relative luminance for both colors
    luminance1 = calculate_relative_luminance(color1)
    luminance2 = calculate_relative_luminance(color2)

    # Ensure that the lighter color's luminance is in luminance1
    if luminance2 > luminance1:
        luminance1, luminance2 = luminance2, luminance1

    # Calculate contrast ratio with "+ 0.05" for adjustment
    return (luminance1 + 0.05) / (luminance2 + 0.05)

def calculate_relative_luminance(color):
    """
    Calculate the relative luminance of a color using the formula:
    L = 0.2126 * R + 0.7152 * G + 0.0722 * B
    
    Args:
        color (Color): A color object.
        
    Returns:
        float: The relative luminance of the color."""
    r, g, b = color.rgb

    # Calculate relative luminance using the specified formula
    return 0.2126 * r + 0.7152 * g + 0.0722 * b