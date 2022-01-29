from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt, QUrl, QStringListModel, QEvent
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QStyle, QPushButton, QLineEdit, QHBoxLayout, QSlider, QVBoxLayout, QAction, QMessageBox, QLabel, QListView, QComboBox, QAbstractItemView
import sys
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

import os
import re
from enum import Enum

idMatch = re.compile('^[a-j][1-8]\d{6}$')
langMatch = re.compile("^((國|台|粵|日|英|客|韓)語|兒歌|其他|原住民)$")


class Lang(Enum):
    NONE = ' '
    CHINESE = 'a'
    TAIWANESE = 'b'
    HK = 'c'
    JAPANESE = 'd'
    ENGLISH = 'e'
    HAKKA = 'f'
    ORIGINAL = 'g'
    KOREAN = 'h'
    CHILDREN = 'i'
    OTHER = 'j'


class SingerType(Enum):
    NONE = 0
    FEMALE = 1
    MALE = 2
    GROUP = 3
    TOGATHER = 4
    FOREIGN_FEMALE = 5
    FOREIGN_MALE = 6
    FOREIGN_GROUP = 7
    OTHER = 8


langs = {
    Lang.NONE: '不考慮',
    Lang.CHINESE: '國語',
    Lang.TAIWANESE: '台語',
    Lang.HK: '粵語',
    Lang.JAPANESE: '日語',
    Lang.ENGLISH: '英語',
    Lang.HAKKA: '客語',
    Lang.ORIGINAL: '原住民語',
    Lang.KOREAN: '韓語',
    Lang.CHILDREN: '兒歌',
    Lang.OTHER: '其他',
}

singerTypes = {
    SingerType.NONE: "不考慮",
    SingerType.FEMALE: "國語女歌手",
    SingerType.MALE: "國語男歌手",
    SingerType.GROUP: "國語團體",
    SingerType.TOGATHER: "合唱",
    SingerType.FOREIGN_FEMALE: "外語女歌手",
    SingerType.FOREIGN_MALE: "外語男歌手",
    SingerType.FOREIGN_GROUP: "外語團體",
    SingerType.OTHER: "其他",
}


class Singer():
    def __init__(self, name, gender, singerType):
        self.name = name
        self.gender = gender
        self.singerType = singerType


class Song():
    def __init__(self, path, id, lang, singer, name):
        self.path = path
        self.name = name
        self.id = id
        self.lang = Lang(id[0])
        self.singer = singer
        self.singerType = SingerType(int(id[1]))

    def output_csv(self):
        return self.id + "," + langs[self.lang] + "," + self.name + "," + self.singer + ',' + singerTypes[self.singerType] + "," + self.path


def check_filename(basename, extension):

    if extension != ".mp4":
        print("%s is not mp4" % basename)
        return False

    strs = basename.split("_")

    if len(strs) < 4:
        print("%s format isn't correct" % basename)
        return False

    if idMatch.match(strs[0]) is None:
        print("%s id is not ok" % basename)
        return False

    if langMatch.match(strs[1]) is None:
        print("%s lang is not ok" % basename)
        return False

    return True


def list_all_songs(path):
    path = os.path.abspath(path)
    print("Songs abspath: %s" % path)

    songs = []

    for (dirpath, dirnames, filenames) in os.walk(path):

        for filename in filenames:
            songpath = os.path.join(dirpath, filename)
            print("songpath is %s" % songpath)

            basename = os.path.splitext(filename)[0]
            extension = os.path.splitext(filename)[1]

            if check_filename(basename, extension) is False:
                continue

            strs = basename.split("_")

            songs.append(Song(songpath, strs[0], strs[1], strs[2], strs[3]))

        break  # do 1 time for iterate 1 layer (level)

    return songs


def output_csv(songs):
    outF = open("myOutFile.csv", "w", encoding='utf8')

    for song in songs:
        outF.write(song.output_csv())
        outF.write("\n")

    outF.close()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.get_songs_path_from_input_dialog()

        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)

        # hbox (parent)
        hbox = QHBoxLayout()

        # column 1: play list widget
        self.playListWidget = PlayListWidget(self)
        hbox.addWidget(self.playListWidget)

        # column 2: searching list Widget
        self.searchListWidget = SearchListWidget(self)
        hbox.addWidget(self.searchListWidget)

        # set parent layout
        self.setLayout(hbox)

    def get_songs_path_from_input_dialog(self):
        songsPath = QFileDialog.getExistingDirectory(
            self, "請選擇歌庫路徑")

        self.songs = list_all_songs(songsPath)
        output_csv(self.songs)

    def closeEvent(self, event: QEvent):
        close = QMessageBox()
        close.setText("你確定要離開嗎?")
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        close = close.exec()

        if close == QMessageBox.Yes:
            event.accept()
            self.playListWidget.close_player()
        else:
            event.ignore()


class PlayListWidget(QWidget):
    def __init__(self, mainWindow: MainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        self.playerWindow = PlayerWindow(self)
        self.playerWindow.show()

        self.selectedSongIndex = -1

        self.playList = []  # songs will be played
        # self.playList = self.mainWindow.songs.copy()

        # column 1
        column1 = QVBoxLayout()

        # column 1, play list view
        self.playListView = QListView()
        self.playListView.setModel(QStringListModel())
        self.playListView.clicked.connect(self.on_song_item_selected)
        column1.addWidget(self.playListView)
        self.playListView.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)

        # column 1, button bar
        buttonBar = QHBoxLayout()
        column1.addLayout(buttonBar)

        # column 1, button bar, insert button
        self.insertBtn = QPushButton("插播")
        self.insertBtn.clicked.connect(self.on_insert_btn_clicked)
        buttonBar.addWidget(self.insertBtn)

        # column 1, button bar, remove button
        self.removeBtn = QPushButton("移除")
        self.removeBtn.clicked.connect(self.on_remove_btn_clicked)
        buttonBar.addWidget(self.removeBtn)

        # column 1, button bar, cut button
        self.cutBtn = QPushButton("切歌")
        self.cutBtn.clicked.connect(self.on_cut_btn_clicked)
        buttonBar.addWidget(self.cutBtn)

        self.setLayout(column1)

        self.update_play_list_view()

    def add_song(self, song: Song):

        if self.playerWindow.is_playing() is False and not self.playList:
            self.playerWindow.load_and_paly_video(song)
        else:
            self.playList.append(song)
            self.update_play_list_view()

    def next_song(self):
        if self.playList:
            print("next song")
            song = self.playList[0]
            del self.playList[0]
            self.playerWindow.load_and_paly_video(song)
            self.update_play_list_view()
        else:
            QMessageBox.information(self, "Hello", "歌單空了喔！！")
            print("play list empty")

    def on_song_item_selected(self, modelIndex):
        self.selectedSongIndex = modelIndex.row()

    def on_insert_btn_clicked(self):
        if self.selectedSongIndex == -1:
            QMessageBox.information(self, '錯誤', '請選擇歌曲後才能插播')
        else:
            song = self.playList[self.selectedSongIndex]
            del self.playList[self.selectedSongIndex]
            self.playList.insert(0, song)
            self.selectedSongIndex = -1
            self.update_play_list_view()

    def on_remove_btn_clicked(self):
        if self.selectedSongIndex == -1:
            QMessageBox.information(self, '錯誤', '請選擇歌曲後才能移除')
        else:
            del self.playList[self.selectedSongIndex]
            self.selectedSongIndex = -1
            self.update_play_list_view()

    def on_cut_btn_clicked(self):
        if self.playerWindow.is_playing():
            self.playerWindow.mediaPlayer.stop()
        else:
            QMessageBox.information(self, '錯誤', '沒有歌曲再撥放喔！')

    def update_play_list_view(self):
        stringList = []

        for song in self.playList:
            stringList.append(song.name)

        self.playListView.model().setStringList(stringList)

    def close_player(self):
        self.playerWindow.close()


class SearchListWidget(QWidget):
    def __init__(self, mainWindow: MainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        self.selectedSong = None

        # self.searchList = []
        self.searchList = self.mainWindow.songs.copy()

        # hbox (parent layout)
        hbox = QHBoxLayout()

        # column 2
        column2 = self.create_column2()
        hbox.addLayout(column2)

        # add parent layout
        self.setLayout(hbox)

        self.update_search_list_view()

    def check_song_correct_or_not(self, song: Song):
        if self.singerEdit.text().upper() not in song.singer.upper():
            return False

        if self.songNameEdit.text().upper() not in song.name.upper():
            return False

        if self.idEdit.text().upper() not in song.id.upper():
            return False

        currentSingerType = list(SingerType)[self.singerTypeBox.currentIndex()]

        if currentSingerType is not song.singerType and currentSingerType is not SingerType.NONE:
            return False

        currentLang = list(Lang)[self.langBox.currentIndex()]

        if currentLang is not song.lang and currentLang is not Lang.NONE:
            return False

        return True

    def check_every_songs_correct_or_not(self):
        self.searchList = list(
            filter(self.check_song_correct_or_not, self.mainWindow.songs))

        self.update_search_list_view()

    def on_edit_text_changed(self, str):
        self.check_every_songs_correct_or_not()

    def on_singer_type_box_index_changed(self, index):
        self.check_every_songs_correct_or_not()

    def create_column2(self):
        # VBox
        vbox = QVBoxLayout()

        # HBox id
        hboxId = QHBoxLayout()
        vbox.addLayout(hboxId)

        # HBox id, label
        idLabel = QLabel()
        idLabel.setText("歌號：")
        hboxId.addWidget(idLabel)

        # HBox id, Line edit
        self.idEdit = QLineEdit()
        self.idEdit.textChanged.connect(self.on_edit_text_changed)
        hboxId.addWidget(self.idEdit)

        # HBox lang
        hboxLang = QHBoxLayout()
        vbox.addLayout(hboxLang)

        # HBox lang, label
        langLabel = QLabel()
        langLabel.setText("語言：")
        hboxLang.addWidget(langLabel)

        # HBox lang, combobox
        self.langBox = QComboBox()
        self.langBox.addItems(
            list(map(lambda x: langs[x], Lang)))
        self.langBox.currentIndexChanged.connect(
            self.on_singer_type_box_index_changed)
        hboxLang.addWidget(self.langBox)

        # HBox singerType
        hboxSingerType = QHBoxLayout()
        vbox.addLayout(hboxSingerType)

        # HBox singerType, label
        singerTypeLabel = QLabel()
        singerTypeLabel.setText("歌手類型：")
        hboxSingerType.addWidget(singerTypeLabel)

        # HBox singerType, combobox
        self.singerTypeBox = QComboBox()
        self.singerTypeBox.addItems(
            list(map(lambda x: singerTypes[x], SingerType)))
        self.singerTypeBox.currentIndexChanged.connect(
            self.on_singer_type_box_index_changed)
        hboxSingerType.addWidget(self.singerTypeBox)

        # HBox singer
        hbox1 = QHBoxLayout()
        vbox.addLayout(hbox1)

        # HBox singer, label
        singerLabel = QLabel()
        singerLabel.setText("歌手：")
        hbox1.addWidget(singerLabel)

        # HBox singer, line edit
        self.singerEdit = QLineEdit()
        self.singerEdit.textChanged.connect(self.on_edit_text_changed)
        hbox1.addWidget(self.singerEdit)

        # HBox song name
        hbox2 = QHBoxLayout()
        vbox.addLayout(hbox2)

        # HBox song name, label
        songNameLabel = QLabel()
        songNameLabel.setText("歌名：")
        hbox2.addWidget(songNameLabel)

        # HBox song name, line edit
        self.songNameEdit = QLineEdit()
        self.songNameEdit.textChanged.connect(self.on_edit_text_changed)
        hbox2.addWidget(self.songNameEdit)

        # search list view
        self.searchListView = QListView()
        self.searchListView.setModel(QStringListModel())
        self.searchListView.clicked.connect(self.on_song_item_selected)
        self.searchListView.doubleClicked.connect(
            self.on_song_item_double_clicked)
        self.searchListView.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        vbox.addWidget(self.searchListView)

        # select button
        self.selectBtn = QPushButton("點歌")
        self.selectBtn.clicked.connect(self.on_select_btn_clicked)
        vbox.addWidget(self.selectBtn)

        return vbox

    def on_song_item_double_clicked(self, modelIndex):
        self.mainWindow.playListWidget.add_song(
            self.searchList[modelIndex.row()])
        self.selectedSong = None

    def on_song_item_selected(self, modelIndex):
        self.selectedSong = self.searchList[modelIndex.row()]
        print(self.selectedSong.name)

    def on_select_btn_clicked(self):
        if self.selectedSong is None:
            QMessageBox.information(self, '錯誤', '請選擇歌曲後才能點歌')
        else:
            self.mainWindow.playListWidget.add_song(self.selectedSong)
            self.selectedSong = None

    def update_search_list_view(self):
        stringList = []

        for song in self.searchList:
            stringList.append(song.name)

        self.searchListView.model().setStringList(stringList)


class PlayerWindow(QWidget):
    def __init__(self, playListWidget: PlayListWidget):
        super().__init__()

        # self.setWindowIcon()
        self.setWindowTitle("Hello world!")
        self.setGeometry(350, 100, 700, 500)

        self.playListWidget = playListWidget

        self.setWindowFlags(Qt.WindowType.Window
                            | Qt.WindowType.WindowMinimizeButtonHint
                            | Qt.WindowType.WindowMaximizeButtonHint)

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
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(song.path)))
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
            self.playListWidget.next_song()
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())
