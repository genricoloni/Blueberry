"""
Module for handling the system environment and wallpaper management based on song changes.
"""
import os

class Handler:
    """
    A class that handles the system environment and wallpaper management based on song changes.

    The Handler class is responsible for detecting the system environment, checking song status,
    managing wallpaper settings, and restoring or setting wallpapers based on current song changes.

    Attributes:
        song_id (str): The ID of the currently playing song.
        playing (bool): A flag indicating whether the song is currently playing or paused.
        available_environments (list): A list of available environments to interact with.
        favorites (dict): A dictionary of saved favorite album configurations.
        environment (str): The current environment name.
        command (str): The command used to change the wallpaper.
        original_wallpaper (str): The original wallpaper to restore.
    """

    # pylint: disable=C0301
    def __init__(self):
        """
        Initialize the Handler instance.

        This method sets up the default values for `song_id` and `playing`,
        checks the available environment
        loads the favorites, and determines the current environment, 
        command, and original wallpaper.
        """
        self.song_id = None
        self.playing = False

        self.available_environments = [
            {'envName': 'gnome',
             'testCommand': 'gnome-session',
             'command': 'gsettings set org.gnome.desktop.background picture-uri ' if ('dark' if 'dark' in (os.popen("gsettings get org.gnome.desktop.interface color-scheme").read()) else 'light') == 'light' else 'gsettings set org.gnome.desktop.background picture-uri-dark ',
             'wallpaperPath': os.popen("gsettings get org.gnome.desktop.background picture-uri-dark").read() if 'dark' in (os.popen("gsettings get org.gnome.desktop.interface gtk-theme").read()) else os.popen("gsettings get org.gnome.desktop.background picture-uri").read()
             }
        ]
        self.favorites = self.load_favorites()
        self.environment, self.command, self.original_wallpaper = self.get_environment()

        if not self.environment or not self.command or not self.original_wallpaper:
            raise EnvironmentError("Environment not supported")

    def get_environment(self):
        """
        Detect the current environment (e.g., GNOME).

        This method checks the available environments by running their respective test commands. 
        If the environment is detected, it returns the environment name, the wallpaper command, 
        and the original wallpaper path.

        Returns:
            tuple: A tuple containing the environment name (str), the wallpaper command (str),
            and the original wallpaper path (str).
        """
        for env in self.available_environments:
            result = os.popen(env['testCommand']).read().strip()
            if not result:
                return env['envName'], env['command'], os.popen("gsettings get org.gnome.desktop.background picture-uri-dark").read().strip() if 'dark' in (os.popen("gsettings get org.gnome.desktop.interface color-scheme").read()) else os.popen("gsettings get org.gnome.desktop.background picture-uri").read()
        return None, None, None

    def previous_song(self):
        """
        Check the previous song.

        This method returns the song_id of the previously played song to compare with the current one.

        Returns:
            str: The ID of the previous song.
        """
        return self.song_id

    def is_paused(self):
        """
        Check if the current song is paused.

        This method returns the playing status to determine if the song is paused.

        Returns:
            bool: True if the song is paused, False if it is playing.
        """
        return self.playing

    def change_song(self, song_id):
        """
        Update the current song ID.

        This method updates the song_id to the new song's ID when the song changes.

        Parameters:
            song_id (str): The ID of the new song.
        """
        self.song_id = song_id

    def change_status(self, status):
        """
        Update the playing status of the current song.

        This method changes the status of the song to either playing or paused.

        Parameters:
            status (bool): The new status of the song (True for playing, False for paused).
        """
        self.playing = status

    def set_paused(self):
        """
        Set the song as paused.

        This method sets the playing status of the song to paused.
        """
        self.playing = "False"

    def load_favorites(self):
        """
        Load saved favorite album configurations.

        This method loads previously saved configurations from the `src/savedConfigs` directory
        and returns a dictionary of album IDs and modes.

        Returns:
            dict: A dictionary where keys are album IDs and values are the modes.
        """
        path = "src/savedConfigs"

        if not os.path.exists(path):
            os.makedirs(path)
            return []

        files = os.listdir(path)
        favorites = {}

        for file in files:
            album_id, mode = file.split(".")[0].split("-")
            favorites[album_id] = mode

        return favorites

    def restore_wallpaper(self):
        """
        Restore the original wallpaper.

        This method restores the desktop wallpaper to the original one before any song change.
        """
        os.system(f"{self.command}{self.original_wallpaper}")

    def set_wallpaper(self, path="ImageCache/finalImage.png"):
        """
        Set a new wallpaper based on the current song.

        This method updates the desktop wallpaper to the generated image associated with the current song.
        """
        print(f"{self.command}" + os.path.abspath(path))
        os.system(f"{self.command}" + os.path.abspath(path))

    def same_song(self, song_id):
        """
        Check if the current song is the same as the previous one.

        This method compares the new song's ID with the stored song_id to determine if the song has changed.

        Parameters:
            song_id (str): The ID of the current song.

        Returns:
            bool: True if the song_id matches the previous song, False otherwise.
        """
        return self.song_id == song_id
