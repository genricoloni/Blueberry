import requests
from bs4 import BeautifulSoup
import re
import urllib.request
import io
import gzip

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
            raise Exception(f"Errore nella richiesta: {response.status_code}")
        
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
        try:
            # Crea un oggetto Request con intestazioni personalizzate
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
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
        except urllib.error.URLError as e:
            print(f"URL error: {e}")
            return None
        except urllib.error.HTTPError as e:
            print(f"HTTP error: {e}")
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
            if 'Genius' in artist:
                continue
            else:
                song = s
                break

        # Retrieve the lyrics of the song
        lyric = self.retrieve_lyric(song["url"])

        if lyric:
            #salva il testo in un file txt
            return lyric
        else:
            print("Testo non trovato.")
            return None

    def find_most_relevant_part(self, lyric):
        """Trova la parte più rilevante del testo basata sul chorus escludendo altre sezioni."""
        # Regex per estrarre il testo tra [Chorus] e la prossima sezione, doppio a capo, o fine del testo
        chorus_pattern = re.compile(r'\[Chorus[^\]]*?\](.*?)(?=\[|\n\n|$)', re.IGNORECASE | re.DOTALL)
        
        match = chorus_pattern.search(lyric)
        if match:
            chorus_lyrics = match.group(1).strip()

            print(chorus_lyrics)

            return self.reduce_if_double(chorus_lyrics)
        
        # Se non trova un chorus, cerca per "Bridge"
        bridge_pattern = re.compile(r'\[Bridge.*?\](.*?)(?:\[(?!Bridge).*?\]|\n\n|$)', re.IGNORECASE | re.DOTALL)
        bridge_match = bridge_pattern.search(lyric)
        if bridge_match:
            bridge_lyrics = bridge_match.group(1).strip()
            

            return self.reduce_if_double(bridge_lyrics)
        
        # Se non trova un bridge, cerca per "Verse"
        verse_pattern = re.compile(r'\[Verse.*?\](.*?)(?:\[(?!Verse).*?\]|\n\n|$)', re.IGNORECASE | re.DOTALL)
        verse_match = verse_pattern.search(lyric)
        if verse_match:
            verse_lyrics = verse_match.group(1).strip()

            return self.reduce_if_double(verse_lyrics)
        
        # Se non trova un verso, restituisce le due sezioni più ripetute come potenziali ritornelli
        repeated_section = self.find_repeated_section(lyric)
        if repeated_section:

            return self.reduce_if_double(repeated_section)
                
        return None



    def find_repeated_section(self, lyric):
        """Trova le due sezioni più ripetute nel testo come potenziali ritornelli."""
        # Rimuovi i caratteri speciali e le maiuscole
        clean_lyric = re.sub(r'[^\w\s]', '', lyric).lower()
        
        # Dividi il testo in frasi
        phrases = clean_lyric.split('\n')

        # Conta le occorrenze di ogni frase
        phrase_counts = {}
        for phrase in phrases:
            phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1

        # Ordina le frasi per numero di occorrenze
        sorted_phrases = sorted(phrase_counts, key=phrase_counts.get, reverse=True)

        # Restituisci le due frasi più ripetute
        if len(sorted_phrases) >= 2:
            return sorted_phrases[0] + '\n' + sorted_phrases[1]
        else:
            return None

    def reduce_if_double(self, lyric):
        """Riduce il testo se contiene due sezioni uguali."""
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


def main():
    lf = LyricFinderClient()
    lyric = lf.get_lyric("")
    if lyric:
        #print("Lyric found:", lyric)
        print("Most relevant part:", lf.find_most_relevant_part(lyric))
    lf.close()

if __name__ == "__main__":
    print("Esecuzione del modulo come script")
    main()