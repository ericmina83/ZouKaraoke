from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QAudio
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QWidget, QFileDialog, QStyle, QPushButton, QHBoxLayout, QSlider, QVBoxLayout
import sys
from os import path
from ReadSongs import *


class PlayerWindow(QWidget):
    def __init__(self):
        super().__init__()

        # self.setWindowIcon()
        self.setWindowTitle("Hello world!")
        self.setGeometry(350, 100, 700, 500)

        self.playing = False

        p = self.palette()
        p.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.red)
        self.setPalette(p)

        self.create_player()

    def load_and_paly_video(self, song: Song):
        self.song = song
        mediaContent = QMediaContent(QUrl.fromLocalFile(song.path))
        self.mediaPlayer.setMedia(mediaContent)
        self.playBtn.setEnabled(True)
        self.play_video()

    def play_video(self):
        if self.mediaPlayer.state() == QMediaPlayer.State.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediastate_changed(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.State.PlayingState:
            self.playBtn.setIcon(self.style().standardIcon(
                QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.playBtn.setIcon(self.style().standardIcon(
                QStyle.StandardPixmap.SP_MediaPlay))

        if self.mediaPlayer.state() == QMediaPlayer.State.StoppedState:
            self.playing = False
        else:
            self.playing = True

    def position_changed(self, position):
        self.slider.setValue(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def create_player(self):
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.Flag.VideoSurface)

        videoWidget = QVideoWidget()

        # play vidoe button
        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_MediaPlay))
        self.playBtn.clicked.connect(self.play_video)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.playBtn)
        hbox.addWidget(self.slider)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(videoWidget)
        vbox.addLayout(hbox)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)

        self.setLayout(vbox)
