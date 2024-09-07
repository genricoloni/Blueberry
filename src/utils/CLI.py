import os

class CLI:
    def __init__(self, spotify_client, wallpaper_generator, modes, stop_event):
        self.spotify_client = spotify_client
        self.wallpaper_generator = wallpaper_generator
        self.modes = modes
        self.stop_event = stop_event

    def run(self):
        """
        Command Line Interface for the SpotifySyncWall program.

        The CLI allows the user to change the settings and exit the program.
        """
        while True:
            #clear the screen
            #os.system("clear")

            print("Welcome to the SpotifySyncWall CLI!")
            print("Type 'help' for a list of commands. \n")

            command = input("Enter a command: ")
            print()

            if command == "help":
                print("Commands:")
                print("   help - Display a list of commands.")
                print("   exit - Exit the program.")
                print("   settings - Change the settings.")
                print("   fav - Add this configuration to favorites. This will apply to every song with the same album cover.")

                #wait for the user to press enter
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
                if not saveConfig():
                    input("Press Enter to continue...")
                    continue
                print("Configuration saved.")
                input("Press Enter to continue...")
                continue


    def modify_modes(self):
        """
        Modifica le modalità disponibili per la generazione del wallpaper.
        """
        print("Modalità disponibili:")
        print("  1. Gradient")
        print("  2. Blurred")
        print("  3. Waveform")
        print("  4. Album Image")
        print("  5. Controller Image")

        choice = input("Scegli le modalità (separate da virgole): ")
        selected_modes = choice.replace(" ", "").split(",")

        new_modes = []
        for mode in selected_modes:
            if mode == "1":
                new_modes.append("gradient")
            elif mode == "2":
                new_modes.append("blurred")
            elif mode == "3":
                new_modes.append("waveform")
            elif mode == "4":
                new_modes.append("albumImage")
            elif mode == "5":
                new_modes.append("controllerImage")
            else:
                print(f"Modalità non valida: {mode}")

        if new_modes:
            self.modes.clear()
            self.modes.extend(new_modes)
            print(f"Nuove modalità impostate: {self.modes}")
        else:
            print("Nessuna modalità valida selezionata.")
    
    def show_help(self):
        """
        Mostra la lista dei comandi disponibili.
        """
        print("Comandi disponibili:")
        print("  help - Mostra questo messaggio di aiuto")
        print("  settings - Cambia le modalità di wallpaper")
        print("  exit - Esce dal programma")

    def saveConfig(self):
        """
        Copy the current configuration to the 'savedConfigs' folder.
        """
        #copy ImageCache/finalImage.png to src/savedConfigs/songID-MODE.png
        with open("src/songCheck.txt", "r") as f:
            lines = f.readlines()
            f.close()
        #get the album cover url
        songID, mode = lines[0].strip(), lines[1].strip()
        #copy the image
        os.system(f"cp ImageCache/finalImage.png src/savedConfigs/{songID}-{mode}.png")
