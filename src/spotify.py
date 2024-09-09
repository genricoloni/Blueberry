import requests
from cachetools import TTLCache
from spotipy import util
import json
from urllib.parse import urlencode
import time


class SpotifyClient:
    """
    A class representing a client for interacting with the Spotify API.

    This client allows authentication and retrieval of the currently playing song for a specific user.

    Attributes:
        client_id (str): The client ID for Spotify API authentication.
        client_secret (str): The client secret for Spotify API authentication.
        username (str): The username associated with the Spotify account.
        scope (str): The access scope for the Spotify API.
        token (str): The authentication token for API requests.
        maxTries (int): The maximum number of attempts for API requests in case of failure.
        retryDelay (int): The delay between retries for API requests.
    """

    def __init__(self, client_id, client_secret, username):
        """
        Initialize a new instance of the SpotifyClient class.

        This method sets up the basic parameters required for authentication and
        calls the authenticate method to obtain the access token.

        Parameters:
            client_id (str): The client ID for Spotify API authentication.
            client_secret (str): The client secret for Spotify API authentication.
            username (str): The username associated with the Spotify account.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.scope = "user-read-currently-playing"
        self.token = None
        self.maxTries = 3
        self.retryDelay = 5
        self.authenticate()

    def authenticate(self):
        """
        Authenticate the client with the Spotify API.

        This method requests an authentication token using the provided client credentials
        and user information. It raises an exception if authentication fails.
        """
        self.token = util.prompt_for_user_token(self.username,
                                                self.scope,
                                                self.client_id,
                                                self.client_secret,
                                                redirect_uri="https://www.google.com/")
        
        if not self.token:
            raise Exception("Error while authenticating")

    def get_current_song(self):
        """
        Retrieve the currently playing song from Spotify.

        This method sends a request to the Spotify API to fetch the currently playing
        song for the authenticated user. It retries the request in case of errors
        up to `maxTries` times.

        Returns:
            dict: A dictionary containing song details, such as song title, artist name,
            album image URL, song ID, song length, and playing status. If no song is playing,
            or the request fails, it returns None.
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
                        "songTitle": name,
                        "artistName": artistName,
                        "imageUrl": imageUrl,
                        "songID": songID,
                        "songLength": songLength,
                        "playing": status
                    }

                    # Check if all data values are valid
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
