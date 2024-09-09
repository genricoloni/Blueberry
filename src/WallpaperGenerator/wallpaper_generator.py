import os
from utils.cache import cacheManager
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import colorgram
import random
import utils.spotify

import utils.images as images

from WallpaperGenerator.album_image import create_album_image as cai

from WallpaperGenerator.gradient import generate_gradient_image as csi

from WallpaperGenerator.blurred import create_blurred_image as cbi

from WallpaperGenerator.waveform import create_waveform_image as cwi

from WallpaperGenerator.controller import create_controller_image as cci

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
        self.current_mode = None
        self.cacheManager = cacheManager()
        self.changedModes = False

    def get_current_album(self):
        """
        Get the details of the currently playing song.

        Returns:
            dict: A dictionary containing details of the currently playing song (title, artist, image URL).
        """
        return self.now_showing
    
    def set_current_album(self, song_id):
        """
        Set the details of the currently playing song.

        Parameters:
            song_details (dict): A dictionary containing details of the song (title, artist, image URL).
        """
        self.now_showing = song_id

    def get_current_mode(self):
        """
        Get the current wallpaper mode.

        Returns:
            str: The current wallpaper mode.
        """
        return self.current_mode
    
    def set_current_mode(self, mode):
        """
        Set the current wallpaper mode.

        Parameters:
            mode (str): The new wallpaper mode.
        """
        self.current_mode = mode

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
        text = images.generate_text_image(song_title, artist_name, colors, self.display)

        cai(self.display, image, text, colors)


    def generate_gradient(self, song_details):
        """
        Generate a gradient wallpaper based on the provided song details.

        This method generates a gradient wallpaper using the extracted colors from the album artwork.

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

        image = self.setup_album_image(self.display, image_url)


        csi(colors, self.display, image.width, song_title, artist_name, image)

    def generate_blurred(self, song_details):
        """
        Generate a blurred wallpaper based on the provided song details.

        This method generates a blurred wallpaper using the album artwork.

        Parameters:
            song_details (dict): A dictionary containing details of the song (title, artist, image URL).
        """

        if song_details == self.now_showing:
            return

        cover_image = Image.open(io.BytesIO(self.cacheManager.get(song_details['imageUrl'])))

        cbi(cover_image, self.display)

    def generate_waveform(self, spotify_client, song_details):
        """
        Generate a waveform wallpaper based on the provided song details.

        This method generates a waveform wallpaper using the album artwork.

        Parameters:
            song_details (dict): A dictionary containing details of the song (title, artist, image URL).
        """
        
        audio_analysis = spotify_client.get_audio_analysis(song_details['songID'])

        if not audio_analysis:
            return
        

        cwi(audio_analysis, 
            self.display, 
            self.cacheManager.get(song_details['imageUrl']),
            song_details['artistName'],
            song_details['songTitle'],
            self.get_colors(song_details['imageUrl']))
        
        
    def generate_controller(self, song_details):
        """
        Generate a controller wallpaper based on the provided song details.

        This method generates a controller wallpaper using the album artwork.

        Parameters:
            song_details (dict): A dictionary containing details of the song (title, artist, image URL).
        """
        song_title = song_details['songTitle']
        artist_name = song_details['artistName']
        image_url = song_details['imageUrl']
        song_length = song_details['songLength']
        colors = self.get_colors(image_url)


        album_image = self.setup_album_image(self.display, image_url)


        cci(song_title, artist_name, image_url, colors, self.display, song_length, album_image)


        
