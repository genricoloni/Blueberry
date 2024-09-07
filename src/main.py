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
    # Inizializza la configurazione
    config_manager = ConfigManager('creds.txt')
    
    # Inizializza il client Spotify
    spotify_client = SpotifyClient(
        client_id=config_manager.get('client_id'),
        client_secret=config_manager.get('client_secret'),
        username=config_manager.get('spot_username'),
    )

    # Inizializza il generatore di wallpaper
    wallpaper_generator = WallpaperGenerator()

    handler = Handler()

    # Flag per comunicare tra i thread
    stop_event = threading.Event()  # Segnala al thread di fermarsi
    modes = ["gradient", "blurred", "waveform", "albumImage", "controllerImage"]  # Modalità correnti

    # Thread per il monitoraggio della musica e la generazione del wallpaper
    wallpaper_thread = threading.Thread(
        target=change_wallpaper_periodically,
        args=(spotify_client, wallpaper_generator, stop_event, modes, handler)
    )

    # Thread per la CLI
    cli_thread = threading.Thread(
        target=start_cli,
        args=(spotify_client, wallpaper_generator, stop_event, modes)
    )

    # Avvia entrambi i thread
    wallpaper_thread.start()
    cli_thread.start()

    # Attendi che il thread della CLI finisca
    cli_thread.join()

    # Una volta terminata la CLI, segnala al thread del wallpaper di fermarsi
    stop_event.set()
    wallpaper_thread.join()

    print("Programma terminato")

def change_wallpaper_periodically(spotify_client, wallpaper_generator, stop_event, modes, handler):
    """
    Questo thread cambia il wallpaper periodicamente basandosi sulla musica in riproduzione su Spotify.
    """
    while not stop_event.is_set():
        try:
            song_details = spotify_client.get_current_song()
            if not song_details:
                print("Nessuna canzone in riproduzione")
                time.sleep(1)
                continue

            #print(f"Canzone corrente: {song_details['name']} - {song_details['artistName']}")

            #print(f"Canzone precedente: {handler.previous_song()}, Stato precedente: {handler.previous_status()}")

            # if the song changed, or if the song was previously paused and now playing
            if handler.previous_song() != song_details["songID"] or (handler.previous_status() == False and song_details["playing"] == True):
                handler.change_song(song_details["songID"])
                handler.change_status(song_details["playing"])
                wallpaper_generator.generate_wallpaper(random.choice(modes), song_details)

                

            
            # Tempo di attesa prima di aggiornare di nuovo il wallpaper
            time.sleep(1)
            #os.system("clear")
        except Exception as e:
            print(f"Errore nella generazione del wallpaper: {e}")
            exit()

def start_cli(spotify_client, wallpaper_generator, stop_event, modes):
    """
    Questo thread gestisce la CLI per cambiare le impostazioni e controllare il programma.
    """
    cli = CLI(spotify_client, wallpaper_generator, modes, stop_event)
    cli.run()

if __name__ == "__main__":
    main()
