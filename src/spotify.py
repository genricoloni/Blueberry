import requests
from cachetools import TTLCache
from spotipy import util
import json
from urllib.parse import urlencode
import time


class SpotifyClient:
    def __init__(self, client_id, client_secret, username):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.scope = "user-read-currently-playing"
        self.token = None
        self.cache = TTLCache(maxsize=100, ttl=3600)
        self.maxTries = 3
        self.retryDelay = 5
        self.authenticate()

    def authenticate(self):
        """
        method to authenticate the client
        """
        self.token = util.prompt_for_user_token(self.username
                                                , self.scope
                                                , self.client_id
                                                , self.client_secret
                                                , redirect_uri="https://www.google.com/")
        
        if not self.token:
            raise Exception("Error while authenticating")
        else:
            print("Authenticated successfully")
        

    def get_current_song(self):
        """
        method to get the current song playing
        """
        header = {"Authorization": f"Bearer {self.token}"}
        url = "https://api.spotify.com/v1/me/player/currently-playing"

        for _ in range(self.maxTries):
            try:
                response = requests.get(url, headers=header)
                if response.status_code == 200:
                    content = json.loads(response.text)

                    status = content.get("is_playing")
                    item = content.get("item")
                    name = item.get("name")
                    artistName = item.get("album").get("artists")[0].get("name")
                    imageUrl = item.get("album").get("images")[0].get("url")
                    songID = item.get("id")
                    songLength = item.get("duration_ms")

                    data = {
                        "name": name,
                        "artistName": artistName,
                        "imageUrl": imageUrl,
                        "songID": songID,
                        "songLength": songLength,
                        "playing": status
                    }

                    #print(f"Current song:", data)

                    # check if everything is present and valid
                    if all(data.values()):
                        return data
                    else:
                        time.sleep(self.retryDelay)
                        continue


                else:
                    return None
            except Exception as e:
                print(f"Error while getting current song: {e}")
                continue