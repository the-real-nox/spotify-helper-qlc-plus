import spotipy
from spotipy import SpotifyOAuth
from dotenv import load_dotenv
from time import sleep
from json import dumps

def main():
    load_dotenv()
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        redirect_uri="http://127.0.0.1:9999/spotipy",
        scope="user-read-playback-state user-read-currently-playing"
    ))
    
    current_id = None
    bpm = None
    name = None
    
    while True:
        song = sp.current_playback()
        
        if current_id is None or song["item"]["id"] != current_id:
            current_id = song["item"]["id"]
            bpm = sp.audio_features(["3n3Ppam7vgaVa1iaRUc9Lp"])[0]
            name = song["item"]["name"]
        
        
        
        print(f"{name}: {bpm}")
        
        sleep(1)
    
    
if __name__ == '__main__' :
    main()