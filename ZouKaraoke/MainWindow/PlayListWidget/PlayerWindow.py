from typing import Callable
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (
    QWidget,
    QStyle,
    QPushButton,
    QHBoxLayout,
    QSlider,
    QVBoxLayout,
    QLabel,
)
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

from ZouKaraoke.Song import *
from ZouKaraoke.Container import Container


class PlayerWindow(QWidget):
    def __init__(self, container: Container):
        super().__init__()

        # self.setWindowIcon()
        self.setWindowTitle("Hello world!")
        self.setGeometry(350, 100, 700, 500)

        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowMaximizeButtonHint
        )

        self.container = container
        p = self.palette()
        p.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.black)
        self.setPalette(p)

        # Get default audio device using PyCAW
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

        # column 1 left side volume slider
        self.leftSideVolumeSlider = QSlider(Qt.Orientation.Vertical)
        self.leftSideVolumeSlider.setRange(0, 100)
        self.leftSideVolumeSlider.sliderMoved.connect(
            self.on_left_side_volume_slider_position_changed
        )
        self.leftSideVolumeSlider.setSliderPosition(
            int(self.volume.GetChannelVolumeLevelScalar(0) * 100)
        )

        # column 2 player
        vbox = self.create_player()

        # column 3 right side volume slider
        self.rightSideVolumeSlider = QSlider(Qt.Orientation.Vertical)
        self.rightSideVolumeSlider.setRange(0, 100)
        self.rightSideVolumeSlider.sliderMoved.connect(
            self.on_right_side_volume_slider_position_changed
        )
        self.rightSideVolumeSlider.setSliderPosition(
            int(self.volume.GetChannelVolumeLevelScalar(1) * 100)
        )

        # hBox (parent)
        hBox = QHBoxLayout()
        hBox.addWidget(self.leftSideVolumeSlider)
        hBox.addLayout(vbox)
        hBox.addWidget(self.rightSideVolumeSlider)

        self.setLayout(hBox)

    def load_and_play_video(self, songVersion: SongVersion):
        self.songNameLabel.setText(songVersion.name)
        self.singerLabel.setText(songVersion.song.get_singers_name())
        print(songVersion.songPath)
        self.mediaPlayer.setMedia(
            QMediaContent(QUrl.fromLocalFile(songVersion.songPath))
        )
        self.playBtn.setEnabled(True)
        self.play_video()

    def play_video(self):
        if self.mediaPlayer.state() == QMediaPlayer.State.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def media_state_changed(self, state):
        if state == QMediaPlayer.State.PlayingState:
            self.playBtn.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
            )
        else:
            self.playBtn.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )

        if state == QMediaPlayer.State.StoppedState:
            print("stopped")
            self.container.eventBus.emit("next_song")
        else:
            print("playing")

    def is_playing(self):
        return self.mediaPlayer.state() != QMediaPlayer.State.StoppedState

    def on_left_side_volume_slider_position_changed(self, position):
        self.volume.SetChannelVolumeLevelScalar(0, position / 100.0, None)  # Left

    def on_right_side_volume_slider_position_changed(self, position):
        self.volume.SetChannelVolumeLevelScalar(1, position / 100.0, None)  # Right

    def position_changed(self, position):
        self.slider.setValue(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def create_player(self):
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.Flag.VideoSurface)

        videoWidget = QVideoWidget()

        # hBox title and singer
        titleSingerWidget = QWidget()
        titleSingerHBox = QHBoxLayout()
        titleSingerHBox.setAlignment(Qt.AlignmentFlag.AlignTop)
        titleSingerHBox.setContentsMargins(0, 0, 0, 0)
        titleSingerWidget.setFixedHeight(40)
        titleSingerWidget.setContentsMargins(0, 0, 0, 0)
        titleSingerWidget.setLayout(titleSingerHBox)

        self.songNameLabel = QLabel("歌名")
        self.songNameLabel.setStyleSheet("QLabel{color: white}")
        self.singerLabel = QLabel("歌手")
        self.singerLabel.setStyleSheet("QLabel{color: white}")

        titleSingerHBox.addWidget(self.songNameLabel)
        titleSingerHBox.addWidget(self.singerLabel)

        # play video button
        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        )
        self.playBtn.clicked.connect(self.play_video)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        hBox = QHBoxLayout()
        hBox.setContentsMargins(0, 0, 0, 0)
        hBox.addWidget(self.playBtn)
        hBox.addWidget(self.slider)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(titleSingerWidget)
        vbox.addWidget(videoWidget)
        vbox.addLayout(hBox)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.media_state_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)

        return vbox
