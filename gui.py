from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6 import uic
import sys


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
        self.waiting(self.bpm, True)
        
    def waiting(self, widget: QLabel, bold: bool = False):
        widget.setText('Waiting...')
        widget.setStyleSheet(widget.styleSheet() + "color: yellow;")
    
    def na(self, widget: QLabel):
        widget.setText('N/A')
        widget.setStyleSheet("color: red;")

app = QApplication(sys.argv)
w = MainWindow()
app.exec()