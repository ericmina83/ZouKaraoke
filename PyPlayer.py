from typing import Callable
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QApplication, QWidget, QStyle, QPushButton, QHBoxLayout, QSlider, QVBoxLayout, QLabel
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from song import *


class PlayerWindow(QWidget):

    next_song_callback: Callable[[], None]

    def __init__(self, next_song_callback: Callable[[], None]):
        super().__init__()

        # self.setWindowIcon()
        self.setWindowTitle("Hello world!")
        self.setGeometry(350, 100, 700, 500)

        self.setWindowFlags(Qt.WindowType.Window
                            | Qt.WindowType.WindowMinimizeButtonHint
                            | Qt.WindowType.WindowMaximizeButtonHint)

        self.next_song_callback = next_song_callback
        p = self.palette()
        p.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.black)
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

    def load_and_play_video(self, songVersion: SongVersion):
        self.songNameLabel.setText(songVersion.name)
        self.singerLabel.setText(songVersion.song.get_singers_name())
        print(songVersion.songpath)
        self.mediaPlayer.setMedia(QMediaContent(
            QUrl.fromLocalFile(songVersion.songpath)))
        self.playBtn.setEnabled(True)
        self.play_video()

    def play_video(self):
        if self.mediaPlayer.state() == QMediaPlayer.State.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediastate_changed(self, state):
        if state == QMediaPlayer.State.PlayingState:
            self.playBtn.setIcon(self.style().standardIcon(
                QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.playBtn.setIcon(self.style().standardIcon(
                QStyle.StandardPixmap.SP_MediaPlay))

        if state == QMediaPlayer.State.StoppedState:
            print("stoped")
            self.next_song_callback()
        else:
            print("playing")

    def is_playing(self):
        return self.mediaPlayer.state() != QMediaPlayer.State.StoppedState

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

        # hbox title and singer
        titleSingerWidget = QWidget()
        titleSingerHbox = QHBoxLayout()
        titleSingerHbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        titleSingerHbox.setContentsMargins(0, 0, 0, 0)
        titleSingerWidget.setFixedHeight(40)
        titleSingerWidget.setContentsMargins(0, 0, 0, 0)
        titleSingerWidget.setLayout(titleSingerHbox)

        self.songNameLabel = QLabel("歌名")
        self.songNameLabel.setStyleSheet("QLabel{color: white}")
        self.singerLabel = QLabel('歌手')
        self.singerLabel.setStyleSheet("QLabel{color: white}")

        titleSingerHbox.addWidget(self.songNameLabel)
        titleSingerHbox.addWidget(self.singerLabel)

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
        vbox.addWidget(titleSingerWidget)
        vbox.addWidget(videoWidget)
        vbox.addLayout(hbox)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)

        return vbox
