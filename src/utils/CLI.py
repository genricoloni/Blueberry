import os

class CLI:
    """
    Command Line Interface for the SpotifySyncWall program.

    This class allows interaction with the user to modify settings, 
    save configurations, and manage the wallpaper generation modes.

    Attributes:
    -----------
    spotify_client : SpotifyClient
        The Spotify client object.
    wallpaper_generator : WallpaperGenerator
        The wallpaper generator object.
    modes : list
        The list of available modes for wallpaper generation.
    stop_event : threading.Event
        The event used to signal when to stop the program.
    """

    def __init__(self, spotify_client, wallpaper_generator, modes, stop_event):
        """
        Initialize the CLI object with required components.

        Parameters:
        -----------
        spotify_client : SpotifyClient
            The Spotify client object.
        wallpaper_generator : WallpaperGenerator
            The wallpaper generator object.
        modes : list
            The list of available modes for wallpaper generation.
        stop_event : threading.Event
            The stop event used to signal termination.
        """
        self.spotify_client = spotify_client
        self.wallpaper_generator = wallpaper_generator
        self.modes = modes
        self.stop_event = stop_event

    def run(self):
        """
        Run the Command Line Interface (CLI).

        This method starts the CLI, allowing the user to input commands 
        to control the settings or exit the program.
        """
        while True:
            # Clear the screen (optional, depends on environment support)
            #os.system("clear")

            print("Welcome to the SpotifySyncWall CLI!")
            print("Type 'help' for a list of commands. \n")
            #print("Now playing: ", self.wallpaper_generator.get_current_album()," in mode: ", self.wallpaper_generator.get_current_mode())

            command = input("Enter a command: ")
            print()

            if command == "help":
                self.show_help()
                input("\nPress Enter to continue...")
                continue

            if command == "exit":
                print("Exiting the program...")
                exit()

            if command == "settings":
                print("Settings:")
                print("  1. Choose which modes to use.")
                setting = input("\nEnter a setting: ")

                if setting == "1":
                    self.modify_modes()
                else:
                    print("Invalid setting.")
                    continue

            if command == "fav":
                if not self.saveConfig():
                    input("Press Enter to continue...")
                    continue
                print("Configuration saved.")
                input("Press Enter to continue...")
                continue

    def modify_modes(self):
        """
        Modify the available wallpaper generation modes.

        Allows the user to select which wallpaper modes to enable from a
        predefined list of modes (gradient, blurred, waveform, etc.).
        """
        print("Available modes:")
        print("\t1. Gradient")
        print("\t2. Blurred")
        print("\t3. Waveform")
        print("\t4. Album Image")
        print("\t5. Controller Image")
        print("\t6. Lyric card")

        choice = input("Choose modes (comma-separated): ")
        selected_modes = choice.replace(" ", "").split(",")

        new_modes = []
        for mode in selected_modes:
            match mode:
                case "1":
                    new_modes.append("gradient")
                case "2":
                    new_modes.append("blurred")
                case "3":
                    new_modes.append("waveform")
                case "4":
                    new_modes.append("albumImage")
                case "5":
                    new_modes.append("controllerImage")
                case "6":
                    new_modes.append("lyricCard")
                case _:
                    print(f"Invalid mode: {mode}")
                    
        if new_modes:
            self.modes.clear()
            self.modes.extend(new_modes)
            print(f"New modes set: {self.modes}")
        else:
            print("No valid modes selected.")
    
    def show_help(self):
        """
        Display the list of available CLI commands.

        This includes commands for viewing help, changing settings, 
        saving favorites, and exiting the program.
        """
        print("Available commands:")
        print("  help - Show this help message.")
        print("  settings - Change the wallpaper generation modes.")
        print("  exit - Exit the program.")
        print("  fav - Add the current configuration to favorites.")
    
    def saveConfig(self):
        """
        Save the current wallpaper configuration.

        Copies the current wallpaper from the cache and stores it in the
        'savedConfigs' folder with a name based on the song's ID and mode.

        Returns:
        --------
        bool
            True if the configuration was saved successfully, False otherwise.
        """
        try:
            #get the current song ID and mode
            songID = self.wallpaper_generator.get_current_album()
            mode = self.wallpaper_generator.get_current_mode()

            #copy the current wallpaper to the savedConfigs folder
            os.system(f"cp ImageCache/finalImage.png src/savedConfigs/{songID}-{mode}.png")
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
