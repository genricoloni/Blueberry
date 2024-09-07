import os

class Handler:
    def __init__(self):
        self.songID = None
        self.playing = False

        self.availableEnvironment = [
            {'envName': 'gnome',
             'testCommand' : 'gnome-session',
             'command' : 'gsettings set org.gnome.desktop.background picture-uri ' if ('dark' if 'dark' in (os.popen("gsettings get org.gnome.desktop.interface gtk-theme").read()) else 'light') == 'light' else 'gsettings set org.gnome.desktop.background picture-uri-dark ',
             'wallpaperPath' : os.popen("gsettings get org.gnome.desktop.background picture-uri-dark").read() if 'dark' in (os.popen("gsettings get org.gnome.desktop.interface gtk-theme").read()) else os.popen("gsettings get org.gnome.desktop.background picture-uri").read()
             }]
        
        self.favorites = self.loadFavorites()
        self.enviroment, self.command, self.originalWallpaper = self.getEnviroment()

        print("original wallpaper: ", self.originalWallpaper)

    def getEnviroment(self):
        for env in self.availableEnvironment:
            result = os.popen(env['testCommand']).read().strip()
            if not result:
                return env['envName'], env['command'], os.popen("gsettings get org.gnome.desktop.background picture-uri-dark").read() if 'dark' in (os.popen("gsettings get org.gnome.desktop.interface gtk-theme").read()) else os.popen("gsettings get org.gnome.desktop.background picture-uri").read()


    def previous_song(self):
        """
        Controlla se la canzone è cambiata.
        """
        return self.songID
    
    def previous_status(self):
        """
        Controlla se la canzone è in riproduzione.
        """
        return self.playing
    
    def change_song(self, songID):
        """
        Cambia la canzone.
        """
        self.songID = songID

    def change_status(self, status):
        """
        Cambia lo stato della canzone.
        """
        self.playing = status

    def loadFavorites(self):
        """
        Carica le configurazioni salvate.
        """
        path = "src/savedConfigs"

        if not os.path.exists(path):
            os.makedirs(path)
            return []
        
        files = os.listdir(path)
        favorites = {}

        for file in files:
            albumID, mode = file.split(".")[0].split("-")
            print(albumID, mode)
            favorites[albumID] = mode

        return favorites
    
    def restoreWallpaper(self):
        """
        Ripristina il wallpaper originale.
        """
        os.system(f"{self.command}{self.originalWallpaper}")