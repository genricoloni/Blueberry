import os

class Handler:
    def __init__(self):
        self.songID = None
        self.playing = False
        self.favorites = self.loadFavorites()

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