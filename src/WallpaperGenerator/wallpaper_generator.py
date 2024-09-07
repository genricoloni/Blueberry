import os

class WallpaperGenerator:
    def __init__(self):
        self.display = os.popen("xrandr").read().split("\n")[2].split()[0].split("x")
        self.now_showing = None
    
    def generate_wallpaper(self, mode, song_details, favorites):
        """
        Genera il wallpaper in base alla modalità specificata.
        """
        
        #check if there exists a saved configuration for this album
        if song_details["songID"] in favorites:
            print("Configuration found for this album.")

            #apply the saved wallpaper

        else:
            print("No saved configuration found.")

            