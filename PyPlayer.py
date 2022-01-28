from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QAudio
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QWidget, QFileDialog, QStyle, QPushButton, QHBoxLayout, QSlider, QVBoxLayout
import sys
from os import path
from ReadSongs import *
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL


class PlayerWindow(QWidget):
    def __init__(self, playListWidget):
        super().__init__()

        # self.setWindowIcon()
        self.setWindowTitle("Hello world!")
        self.setGeometry(350, 100, 700, 500)

        self.playListWidget = playListWidget

        self.playing = False

        p = self.palette()
        p.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.red)
        self.setPalette(p)

        # Get default audio device using PyCAW
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

        # column 1 left side valume slider
        self.leftSideValumeSlider = QSlider(Qt.Orientation.Vertical)
        self.leftSideValumeSlider.setRange(0, 100)
        self.leftSideValumeSlider.sliderMoved.connect(
            self.on_left_side_valume_slider_position_changed)
        self.leftSideValumeSlider.setSliderPosition(
            int(self.volume.GetChannelVolumeLevelScalar(0) * 100))

        # column 2 player
        vbox = self.create_player()

        # column 3 right side valume slider
        self.rightSideValumeSlider = QSlider(Qt.Orientation.Vertical)
        self.rightSideValumeSlider.setRange(0, 100)
        self.rightSideValumeSlider.sliderMoved.connect(
            self.on_right_side_valume_slider_position_changed)
        self.rightSideValumeSlider.setSliderPosition(
            int(self.volume.GetChannelVolumeLevelScalar(1) * 100))

        # hbox (parent)
        hbox = QHBoxLayout()
        hbox.addWidget(self.leftSideValumeSlider)
        hbox.addLayout(vbox)
        hbox.addWidget(self.rightSideValumeSlider)

        self.setLayout(hbox)

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
            self.playListWidget.next_song()
            self.playing = False
        else:
            self.playing = True

    def on_left_side_valume_slider_position_changed(self, position):
        self.volume.SetChannelVolumeLevelScalar(
            0, position / 100., None)  # Left

    def on_right_side_valume_slider_position_changed(self, position):
        self.volume.SetChannelVolumeLevelScalar(
            1, position / 100., None)  # Right

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

        return vbox
