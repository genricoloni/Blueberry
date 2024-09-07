import os
from utils.handler import Handler

class WallpaperGenerator:
    def __init__(self):
        self.display = os.popen("xrandr").read().split("\n")[2].split()[0].split("x")
        self.now_showing = None
    
    def generate_wallpaper(self, mode, song_details, handler):
        """
        Genera il wallpaper in base alla modalità specificata.
        """
        print(f"Generating wallpaper for song: {song_details} in mode: {mode}")
        
        #check if there exists a saved configuration for this album
        if song_details["songID"] in handler.favorites:
            mode = handler.favorites[song_details["songID"]]

            #apply the saved wallpaper

            