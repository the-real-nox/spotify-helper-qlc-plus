from dataclasses import dataclass
import spotipy
from spotipy import SpotifyOAuth
from dotenv import load_dotenv
from time import sleep
from bs4 import BeautifulSoup
from requests import post
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QSlider
from PyQt6 import uic
import sys
from threading import Thread, Event


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

    return SongInfo(foundArtist, foundTitle, int(bpm))

def start_spotify_scanning(window: QMainWindow, runningEvent: Event):
    load_dotenv()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        redirect_uri="http://127.0.0.1:9999/spotipy",
        scope="user-read-playback-state user-read-currently-playing"
    ))
    
    current_id = None
    name = None
    
    while not runningEvent.is_set():
        song = sp.current_playback()
        
        try:
            if current_id is None or song["item"]["id"] != current_id:
                current_id = song["item"]["id"]
                name = song["item"]["name"]
                artists = [ s['name'] for s in song['item']['artists'] ]
                window.reset(window.spotifySong)
                window.spotifySong.setText(f"{name} by {artists[0]}")
                
                window.waiting(window.bpmpSong)
                window.waiting(window.bpm)
                print(f"Change detected: {name}")
                try:
                    info = get_bpm(name, artists)
                    
                    window.reset(window.bpm)
                    
                    window.dmxStrobe.setStyleSheet(window.dmxStrobe.styleSheet() + 'color: cyan;')
                    
                    window.reset(window.bpmpSong)
                    window.bpmpSong.setText(f"{info.track} by {info.artist}")

                    window.bpm.setText(str(info.bpm))
                    window.bpm.setStyleSheet(window.bpm.styleSheet() + "color: magenta;")
                    print(f"From bpm-provider: {info}")
                    
                    hz = info.bpm / 60
                    dmx = round(((hz - 1) / 19) * 254 + 1)
                    
                    window.dmxStrobe.setStyleSheet(window.dmxStrobe.styleSheet() + "color: cyan;")
                    window.dmxStrobe.setText(str(dmx))
                    
                    window.dmxStrobeSlider.setValue(round(dmx / 255 * 100))
                except ValueError:
                    window.na(window.bpm)
                    
                    print("No bpm found!")
        except Exception as e:
            print(e)
            window.na_all()
        
        sleep(1)    

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = uic.loadUi('g.ui', self)

        self.setFixedSize(self.size())
        self.show()

        self.spotifySong = self.findChild(QLabel, 'spotifySong')
        self.waiting(self.spotifySong)
        
        self.bpmpSong = self.findChild(QLabel, 'bpmpSong')
        self.waiting(self.bpmpSong)
        
        self.bpm = self.findChild(QLabel, 'bpm')
        self.waiting(self.bpm)
        
        self.dmxStrobe = self.findChild(QLabel, 'dmxStrobe')
        self.waiting(self.dmxStrobe)
        
        self.dmxStrobeSlider = self.findChild(QSlider, 'dmxStrobeSlider')
        self.dmxStrobeSlider.setValue(0)
        
        self.running_event = Event()
        self.spotify_scanner = Thread(target=start_spotify_scanning, args=[self, self.running_event])
        self.spotify_scanner.start()
        
        
        QApplication.instance().aboutToQuit.connect(self.stop_spotify_scanning)
    
    def stop_spotify_scanning(self):
        self.running_event.set()
        self.spotify_scanner.join()
    
    def waiting(self, widget: QLabel):
        widget.setText('Waiting...')
        widget.setStyleSheet(widget.styleSheet() + "color: yellow;")
    
    def na_all(self):
        self.na(self.spotifySong)
        self.na(self.bpmpSong)
        self.na(self.bpm)
        self.na(self.dmxStrobe)
        self.dmxStrobeSlider.setValue(0)
    
    def reset(self, widget: QLabel):
        widget.setStyleSheet(widget.styleSheet() + "color: #d9d9d9;")
    
    def na(self, widget: QLabel):
        widget.setText('N/A')
        widget.setStyleSheet("color: red;")

if __name__ == '__main__' :
    app = QApplication(sys.argv)
    w = MainWindow()
    app.exec()