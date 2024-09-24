"""
Module for searching and retrieving song lyrics from Genius.
"""

import re
import io
import gzip
import urllib.request

import requests
from bs4 import BeautifulSoup

SEARCH_BASE_URL = "https://genius.com/api/search"
GENIUS_BASE_URL = "https://genius.com"

class LyricFinderClient:
    """Client for searching and retrieving song lyrics from Genius.
    Attributes:
        session (requests.Session): A session object for making HTTP requests.
    """

    def __init__(self):
        self.session = requests.Session()

    def search_songs(self, query):
        """
        Search for songs on Genius using the given query.
        Args:
            query (str): The search query.

        Returns:
            list: A list of song objects.
        """

        response = self.session.get(f"{SEARCH_BASE_URL}?q={query}")
        if response.status_code != 200:
            raise RuntimeError(f"Error searching for songs. Status code: {response.status_code}")

        data = response.json()
        hits = data.get("response", {}).get("hits", [])

        # Filter out only the songs
        songs = [hit["result"] for hit in hits if hit["type"] == "song"]
        return songs

    def retrieve_lyric(self, url):
        """Retrieve the lyrics of a song from the given URL.
        Args:
            url (str): The URL of the song on Genius.

        Returns:
            str: The lyrics of the song
        """

        html = self.get_full_html(url)
        if not html:
            return None

        # Parsing dell'HTML per trovare il testo della canzone
        soup = BeautifulSoup(html, 'html.parser')
        lyrics_divs = soup.find_all("div", {"class": "Lyrics__Container-sc-1ynbvzw-1"})

        lyrics = []
        for lyrics_div in lyrics_divs:
            lyrics.append(lyrics_div.get_text(separator="\n").strip())

        return "\n".join(lyrics)

    def get_full_html(self, url):
        """
        Retrieve the full HTML content of a page.
        
        Args:
            url (str): The URL of the page.
            
        Returns:
            str: The full HTML content of the page."""
        try:
            # Crea un oggetto Request con intestazioni personalizzate
            req = urllib.request.Request(url, headers={
                'User-Agent': """Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
                    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36""",
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            })
            with urllib.request.urlopen(req) as response:
                # Controlla se la risposta è compressa
                if response.info().get('Content-Encoding') == 'gzip':
                    buf = io.BytesIO(response.read())
                    with gzip.GzipFile(fileobj=buf) as f:
                        html = f.read()
                else:
                    html = response.read()

                return html.decode('utf-8')
        except urllib.error.HTTPError as e:
            print(f"HTTP error: {e}")
            return None
        except urllib.error.URLError as e:
            print(f"URL error: {e}")
            return None
        except UnicodeDecodeError as e:
            print(f"Unicode decode error: {e}")
            return None

    def get_lyric(self, query):
        """Search for a song and retrieve its lyrics.
        Args:
            query (str): The search query for the song.
            
            Returns:
            str: The lyrics of the song."""
        songs = self.search_songs(query)
        if not songs:
            print("Nessuna canzone trovata!")
            return None

        # The first song is usually the most relevant
        song = songs[0]

        #if there's 'Genius' in song['primary_artist']['name']}, skip it
        for s in songs:
            artist = str(s['primary_artist']['name'])
            if 'Genius' not in artist:
                song = s
                break

        # Retrieve the lyrics of the song
        lyric = self.retrieve_lyric(song["url"])

        if lyric:
            #salva il testo in un file txt
            return lyric

        print("Testo non trovato.")
        return None

    def find_most_relevant_part(self, lyric):
        """Trova la parte più rilevante del testo basata sul chorus escludendo altre sezioni."""
        # Regex to find the chorus
        chorus_pattern = re.compile(r'\[Chorus[^\]]*?\](.*?)(?=\[|\n\n|$)',
                                    re.IGNORECASE | re.DOTALL)

        match = chorus_pattern.search(lyric)
        if match:
            chorus_lyrics = match.group(1).strip()
            return self.reduce_if_double(chorus_lyrics)

        # If no chorus is found, look for a bridge
        bridge_pattern = re.compile(
            r'\[Bridge.*?\](.*?)(?:\[(?!Bridge).*?\]|\n\n|$)',
                re.IGNORECASE | re.DOTALL)
        bridge_match = bridge_pattern.search(lyric)
        if bridge_match:
            bridge_lyrics = bridge_match.group(1).strip()
            return self.reduce_if_double(bridge_lyrics)

        # If no bridge is found, look for a verse
        verse_pattern = re.compile(
            r'\[Verse.*?\](.*?)(?:\[(?!Verse).*?\]|\n\n|$)',
              re.IGNORECASE | re.DOTALL)
        verse_match = verse_pattern.search(lyric)
        if verse_match:
            verse_lyrics = verse_match.group(1).strip()
            return self.reduce_if_double(verse_lyrics)

        # If no verse is found, look for the most repeated section
        repeated_section = self.find_repeated_section(lyric)
        if repeated_section:
            return self.reduce_if_double(repeated_section)

        return None

    def find_repeated_section(self, lyric):
        """
        Find the two most repeated phrases in the lyric.
        Args:
            lyric (str): The lyrics of the song.
        Returns:
            str: The two most repeated phrases.
        """
        # Remove punctuation and convert to lowercase
        clean_lyric = re.sub(r'[^\w\s]', '', lyric).lower()

        # Divide lyric into phrases
        phrases = clean_lyric.split('\n')

        # Count the number of occurrences of each phrase
        phrase_counts = {}
        for phrase in phrases:
            phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1

        # Order phrases by count
        sorted_phrases = sorted(phrase_counts, key=phrase_counts.get, reverse=True)

        # Return the two most repeated phrases
        if len(sorted_phrases) >= 2:
            return sorted_phrases[0] + '\n' + sorted_phrases[1]
        return None

    def reduce_if_double(self, lyric):
        """Reduce the lyric to half if the two halves are the same.
        Args:
            lyric (str): The lyrics of the song.
        Returns:
            str: The reduced lyrics.
        """
        # Trova il numero di righe
        lines = lyric.split('\n')

        if len(lines) < 2 or len(lines) % 2 != 0:
            return lyric

        # Trova la lunghezza della metà del testo
        half_length = len(lines) // 2

        # Controlla se le due metà sono uguali
        for i in range(half_length):
            if lines[i] != lines[i + half_length]:
                return lyric

        # Se le due metà sono uguali, riduci il testo alla metà
        return '\n'.join(lines[:half_length])

    def close(self):
        """Close the client's session."""
        self.session.close()
