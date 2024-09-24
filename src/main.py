"""
The main module that initializes the application components and starts the necessary threads.

This module sets up the configuration, initializes the Spotify client and the wallpaper
generator, and starts two separate threads: one for monitoring the music and changing
the wallpaper, and another for handling user input via the CLI.
It waits for the CLI thread to finish and then stops the wallpaper thread.

"""


import threading
import time
import random
import sys

from utils.spotify import SpotifyClient
from utils.CLI import CLI
from utils.config import ConfigManager
from utils.handler import Handler
from WallpaperGenerator.wallpaper_generator import WallpaperGenerator

def main():
    """
    The main function that initializes the application components and starts the necessary threads.
    
    This function sets up the configuration, initializes the Spotify client and the wallpaper 
    generator, and starts two separate threads: one for monitoring the music and changing 
    the wallpaper, and another for handling user input via the CLI. 
    It waits for the CLI thread to finish and then stops the wallpaper thread.
    """
    # Initialize configuration
    config_manager = ConfigManager('creds.txt')
    # Initialize Spotify client
    spotify_client = SpotifyClient(
        client_id=config_manager.get('client_id'),
        client_secret=config_manager.get('client_secret'),
        username=config_manager.get('spot_username'),
    )

    # Initialize wallpaper generator
    wallpaper_generator = WallpaperGenerator()

    handler = Handler()

    # Flag for thread communication
    stop_event = threading.Event()  # Signal for the thread to stop
    modes = ["gradient",
             "blurred", 
             "waveform", 
             "albumImage", 
             "controllerImage", 
             "lyric"]
    # Thread for monitoring music and generating wallpaper
    wallpaper_thread = threading.Thread(
        target=change_wallpaper_periodically,
        args=(spotify_client, wallpaper_generator, stop_event, modes, handler)
    )

    # Thread for the CLI
    cli_thread = threading.Thread(
        target=start_cli,
        args=(spotify_client, wallpaper_generator, stop_event, modes)
    )

    # Start both threads
    wallpaper_thread.start()
    cli_thread.start()

    # Wait for the CLI thread to finish
    cli_thread.join()

    # Once the CLI is done, signal the wallpaper thread to stop
    stop_event.set()
    wallpaper_thread.join()

    handler.restoreWallpaper()

    print("Program terminated")


def change_wallpaper_periodically(spotify_client, wallpaper_generator, stop_event, modes, handler):
    """
    Periodically change the wallpaper based on the currently playing song on Spotify.
    
    This function runs in a separate thread. It continuously checks the current song playing on
    Spotify, generates a new wallpaper based on a random mode (gradient, blurred, etc.),
    and updates the desktop wallpaper.
    
    Parameters:
    - spotify_client (SpotifyClient): The client used to fetch the currently playing song.
    - wallpaper_generator (WallpaperGenerator): The generator used to create new wallpapers.
    - stop_event (threading.Event): A signal to stop the thread when set.
    - modes (list): A list of available modes for generating wallpapers.
    - handler (Handler): The handler used for managing wallpapers and tracking song changes.
    """
    old_modes = modes
    while not stop_event.is_set():
        try:
            song_details = spotify_client.get_current_song()
            handler.loadFavorites()

            if not song_details or song_details["playing"] is False:
                handler.restoreWallpaper()
                handler.change_status(False)
                time.sleep(1)
                continue

            if song_details["playing"] is False:
                time.sleep(1)
                continue

            if handler.is_paused() is False and song_details["playing"]:
                handler.change_status(True)
                if handler.same_song(song_details["songID"]):
                    handler.change_song(song_details["songID"])
                    handler.setWallpaper()

            # If the song changed, or if the song was previously paused and is now playing
            if not handler.same_song(song_details["songID"]) or old_modes != modes:
                handler.change_song(song_details["songID"])
                handler.change_status(True)
                old_modes = modes
                wallpaper_generator.set_current_album(song_details["songID"])

                if song_details["songID"] in handler.favorites:
                    # Choose from the favorites with the same albumID
                    path = f"src/savedConfigs/{song_details['songID']}"
                    path += f"-{handler.favorites[song_details['songID']]}.png"
                    handler.setWallpaper(path)
                    time.sleep(1)
                    continue

                # Choose a random mode
                mode = random.choice(modes)

                wallpaper_generator.set_current_mode(mode)


                match mode:
                    case "albumImage":
                        # Create an album image object
                        wallpaper_generator.generate_album_image(song_details)

                    case "gradient":
                        # Create a gradient wallpaper
                        wallpaper_generator.generate_gradient(song_details)

                    case "blurred":
                        # Create a blurred wallpaper
                        wallpaper_generator.generate_blurred(song_details)

                    case "waveform":
                        # Create a waveform wallpaper
                        wallpaper_generator.generate_waveform(spotify_client, song_details)

                    case "controllerImage":
                        # Create a controller image
                        wallpaper_generator.generate_controller(song_details)

                    case "lyric":
                        # Create a lyric wallpaper
                        wallpaper_generator.generate_lyric(song_details)

                handler.setWallpaper()

            # Wait time before updating the wallpaper again
            time.sleep(1)
        except IOError as e:
            print(f"Error generating wallpaper: {e}")
            sys.exit(1)


def start_cli(spotify_client, wallpaper_generator, stop_event, modes):
    """
    Start the CLI for controlling the application and changing settings.
    
    This function runs in a separate thread and provides a command-line interface for user input.
    The user can modify settings such as the wallpaper generation modes and control the program.

    Parameters:
    - spotify_client (SpotifyClient): The client used to interact with Spotify.
    - wallpaper_generator (WallpaperGenerator): The generator used for creating wallpapers.
    - stop_event (threading.Event): A signal to stop the thread when set.
    - modes (list): A list of available modes for generating wallpapers.
    """
    cli = CLI(spotify_client, wallpaper_generator, modes, stop_event)
    cli.run()


if __name__ == "__main__":
    main()
