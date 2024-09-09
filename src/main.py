import threading
import time
import os
import random
from spotify import SpotifyClient
from WallpaperGenerator.wallpaper_generator import WallpaperGenerator
from utils.CLI import CLI
from config import ConfigManager
from utils.handler import Handler

def main():
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
    modes = ["gradient", "blurred", "waveform", "albumImage", "controllerImage"]  # Current modes

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
    This thread periodically changes the wallpaper based on the music playing on Spotify.
    """
    old_modes = modes
    while not stop_event.is_set():
        try:
            song_details = spotify_client.get_current_song()

            if not song_details or song_details["playing"] == False:
                handler.restoreWallpaper()
                handler.change_status(False)

                time.sleep(1)
                continue

            if song_details["playing"] == False:
                time.sleep(1)
                continue

            if handler.is_paused() == False and song_details["playing"]:
                handler.change_status(True)
                if handler.same_song(song_details["songID"]):
                    handler.change_song(song_details["songID"])
                    handler.setWallpaper()

            # if the song changed, or if the song was previously paused and now playing
            if  not handler.same_song(song_details["songID"]) or old_modes != modes:
                handler.change_song(song_details["songID"])
                handler.change_status(True)
                old_modes = modes
                wallpaper_generator.set_current_album(song_details["songID"])

                if song_details["songID"] in handler.favorites:
                    # Apply the saved wallpaper

                    continue

                # Choose a random mode
                mode = random.choice(modes)


                #DEBUG, should be removed
                mode = "waveform"

                wallpaper_generator.set_current_mode(mode)

                if mode == "albumImage":
                    # Create an album image object
                    wallpaper_generator.generate_album_image(song_details)

                elif mode == "gradient":
                    # Create a gradient wallpaper
                    wallpaper_generator.generate_gradient(song_details)

                elif mode == "blurred":
                    # Create a blurred wallpaper
                    wallpaper_generator.generate_blurred(song_details)

                elif mode == "waveform":
                    # Create a waveform wallpaper
                    wallpaper_generator.generate_waveform(song_details)


                handler.setWallpaper()



            
            # Wait time before updating the wallpaper again
            time.sleep(1)
            # os.system("clear")
        except Exception as e:
            print(f"Error generating wallpaper: {e}")
            exit()

def start_cli(spotify_client, wallpaper_generator, stop_event, modes):
    """
    This thread handles the CLI for changing settings and controlling the program.
    """
    cli = CLI(spotify_client, wallpaper_generator, modes, stop_event)
    cli.run()

if __name__ == "__main__":
    main()
