from dataclasses import dataclass
import spotipy
from spotipy import SpotifyOAuth
from dotenv import load_dotenv
from time import sleep
from bs4 import BeautifulSoup
from requests import post
from re import search

@dataclass
class SongInfo:
    artist: str
    track: str
    bpm: int

URL = "https://songbpm.com/searches"
def get_bpm(title: str, artists: list[str] = []):
    res = post(
        URL, 
        data = {
            "query": title + (' '.join(artists[0]) if len(artists) > 0 else '')
        },
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "songbpm.com",
            "Origin": "https://songbpm.com",
            "Refer": "https://songbpm.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        }
    )
    
    soup = BeautifulSoup(res.text, "html.parser")
    first_el = soup.find(lambda tag: tag.text == 'BPM')
    parent = first_el.parent()
    
    bpm = parent[1].text.strip()
    
    metaInfoTags = first_el.find_parents()[2].find_all('div')[2].find_all('p')
    
    foundArtist = metaInfoTags[0].text.strip()
    foundTitle = metaInfoTags[1].text.strip()
    
    if foundTitle != title:
        if len(artists) > 0:
            return get_bpm(title)
        
        raise ValueError('Failed to find bpm!')

    return SongInfo(foundArtist, foundTitle, bpm)

def main():
    load_dotenv()
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        redirect_uri="http://127.0.0.1:9999/spotipy",
        scope="user-read-playback-state user-read-currently-playing"
    ))
    
    current_id = None
    name = None
    
    while True:
        song = sp.current_playback()
        
        if current_id is None or song["item"]["id"] != current_id:
            current_id = song["item"]["id"]
            name = song["item"]["name"]
            artists = [ s['name'] for s in song['item']['artists'] ]
            
            print(f"Change detected: {name}")
            try:
                info = get_bpm(name, artists)
                print(f"From bpm-provider: {info}")
            except ValueError:
                print("No bpm found!")
        
        sleep(1)
    
    
if __name__ == '__main__' :
    main()