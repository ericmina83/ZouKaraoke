from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt, QUrl, QStringListModel, QEvent
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QStyle, QPushButton, QLineEdit, QHBoxLayout, QSlider, QVBoxLayout, QAction, QMessageBox, QLabel, QListView, QComboBox, QAbstractItemView
import sys
from black import diff
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from typing import List
import difflib

import os
import re
from enum import Enum

idMatch = re.compile('^[a-j][0-8]\d{6}$')
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


class SongType(Enum):
    NONE = '無'
    ORIGINAL = '原唱'
    COMPANY = '伴唱'
    LEFT_RIGHT_OLD = ''
    LEFT_RIGHT = '人樂分離'


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
    def __init__(self, name):
        self.name: str = name
        self.songs: list[Song] = []


class Song():

    path: str
    name: str
    n_id: str
    lang: Lang
    singerType: SingerType

    def __init__(self, path, id, lang, singer: Singer, name, song_original_path):

        if song_original_path is None:
            self.path: str = path
            self.name: str = name
            self.id: str = id
            self.lang: Lang = Lang(id[0])
            self.singers: List[Singer] = singer
            self.singerType = SingerType(int(id[1]))
        else:
            self.name: str = name
            self.id: str = ""
            self.lang: Lang = Lang.NONE
            self.singers: List[Singer] = Singer("")
            self.singerType = SingerType.NONE
            self.path = song_original_path

    def get_singers_name(self):
        result = self.singers[0].name
        for i in range(1, len(self.singers)):
            result += '&' + self.singers[i].name
        return result

    def output_csv(self):
        return self.id + "," + langs[self.lang] + "," + self.name + "," + self.get_singers_name() + ',' + singerTypes[self.singerType] + "," + self.path


def check_filename(basename: str, extension: str):

    if extension.upper() != ".mp4".upper():
        print("%s is not mp4" % basename)
        return False

    strs = basename.split("_")

    if len(strs) < 4:
        print("%s format isn't correct" % basename)
        return False

    if idMatch.match(strs[0]) is None:
        print("%s id: %s is not ok" % basename, strs[0])
        return False

    if langMatch.match(strs[1]) is None:
        print("%s lang is not ok" % basename)
        return False

    return True


def diff_two_strings(a: str, b: str) -> float:

    diff_count = 0

    for i, s in enumerate(difflib.ndiff(a, b)):
        if s[0] == ' ':
            diff_count -= 5
        elif s[0] == '-':
            diff_count += 2
        elif s[0] == '+':
            diff_count += 1

    return diff_count


def list_all_songs(path):
    path = os.path.abspath(path)
    print("Songs abspath: %s" % path)

    songs: List[Song] = []
    singers: List[Singer] = []

    for (dirpath, dirnames, filenames) in os.walk(path):

        for filename in filenames:
            songpath = os.path.join(dirpath, filename)

            basename = os.path.splitext(filename)[0]
            extension = os.path.splitext(filename)[1]

            if check_filename(basename, extension) is False:
                continue

            strs = basename.split("_")

            singerStrs = strs[2].replace(' ', '').replace('_', '').split('&')

            targetSinger: List[Singer] = []

            for singerStr in singerStrs:
                if len(singers) == 0:
                    singer = Singer(singerStr)
                    singers.append(singer)
                else:
                    singer = next(
                        (singer for singer in singers if singerStr in singer.name or singer.name in singerStr),
                        None)

                    if singer is None:
                        singer = Singer(singerStr)
                        singers.append(singer)

                targetSinger.append(singer)

            try:
                song = Song(songpath, strs[0], strs[1],
                            targetSinger, strs[3], None)
                songs.append(song)

                for singer in targetSinger:
                    singer.songs.append(song)
            except ValueError:
                print("song %s value error!" % basename)

        break  # do 1 time for iterate 1 layer (level)

    return songs, singers


def output_csv(songs):
    outF = open("myOutFile.csv", "w", encoding='utf8')

    for song in songs:
        outF.write(song.output_csv())
        outF.write("\n")

    outF.close()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.songs: List[Song] = []
        self.singers: List[Singer] = []

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

        self.songs, self.singers = list_all_songs(songsPath)

        # for singer in self.singers:
        #     print(singer.name)
        #     for song in singer.songs:
        #         print("    " + song.name)
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


class NewSongInfoForm(QWidget):
    def __init__(self, mainWindow: MainWindow):
        super().__init__()

        self.singers: List[Singer] = []
        self.songs: List[Song] = []
        self.mainWindow = mainWindow

        hboxTotal = QHBoxLayout()

        songNameSearchVbox = QVBoxLayout()
        hboxSongName = QHBoxLayout()
        self.songNameLineEdit = QLineEdit()
        self.songNameLineEdit.textChanged.connect(
            self.update_songname_list_view)
        hboxSongName.addWidget(QLabel("歌名"))
        hboxSongName.addWidget(self.songNameLineEdit)
        songNameSearchVbox.addLayout(hboxSongName)

        self.songNameListView = QListView()
        self.songNameListView.setModel(QStringListModel())
        self.songNameListView.clicked.connect(self.on_song_selected)
        songNameSearchVbox.addWidget(self.songNameListView)
        hboxTotal.addLayout(songNameSearchVbox)

        singerSearchVBox = QVBoxLayout()
        hboxSinger = QHBoxLayout()
        self.singerLineEdit = QLineEdit()
        self.singerLineEdit.textChanged.connect(self.update_singer_list_view)
        hboxSinger.addWidget(QLabel("歌手"))
        hboxSinger.addWidget(self.singerLineEdit)
        singerSearchVBox.addLayout(hboxSinger)

        self.singerlistview = QListView()
        self.singerlistview.setModel(QStringListModel())
        self.singerlistview.clicked.connect(self.on_singer_selected)
        singerSearchVBox.addWidget(self.singerlistview)
        hboxTotal.addLayout(singerSearchVBox)

        self.setLayout(hboxTotal)

        self.update_songname_list_view('')
        self.update_singer_list_view('')

        for singer in self.mainWindow.singers:
            print(singer.name)

    def update_songname_list_view(self, text: str):
        # self.songs = filter(lambda song: song.name.upper() in text.upper(
        # ) or text.upper() in song.name.upper(), self.mainWindow.songs)

        self.songs = list(sorted(self.mainWindow.songs,
                                 key=lambda song: diff_two_strings(song.name.upper(), text.upper())))

        model: QStringListModel = self.songNameListView.model()
        model.setStringList(
            list(map(lambda song: song.name, self.songs)))

    def on_song_selected(self, modelIndex):
        self.songNameLineEdit.setText(self.songs[modelIndex.row()].name)

    def update_singer_list_view(self, text: str):
        print(text)
        # self.singers = list(filter(
        #     lambda singer: text in singer.name, self.mainWindow.singers))

        self.singers = list(sorted(self.mainWindow.singers,
                                   key=lambda singer: diff_two_strings(singer.name.upper(), text.upper())))

        model: QStringListModel = self.singerlistview.model()
        model.setStringList(
            list(map(lambda singer: singer.name, self.singers)))

    def on_singer_selected(self, modelIndex):
        self.singerLineEdit.setText(self.singers[modelIndex.row()].name)

    def on_save_clicked(self):


class PlayListWidget(QWidget):
    def __init__(self, mainWindow: MainWindow):
        super().__init__()

        self.mainWindow: MainWindow = mainWindow
        self.playerWindow = PlayerWindow(self)
        self.playerWindow.show()
        self.selectedSongIndex = -1

        self.playList: List[Song] = []  # songs will be played
        # self.playList = self.mainWindow.songs.copy()

        # column 1
        column1 = QVBoxLayout()

        self.infoForm = NewSongInfoForm(self.mainWindow)

        # column 1, add song from file
        self.addSongBtn = QPushButton("加入新載歌曲")
        self.addSongBtn.clicked.connect(self.on_add_song_from_file_clicked)
        column1.addWidget(self.addSongBtn)

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

    def on_add_song_from_file_clicked(self):
        filename, _ = QFileDialog.getOpenFileName(self, "載入新檔案")
        if filename != '':
            self.infoForm.songPath = filename
            self.infoForm.show()
            # basename = os.path.splitext(os.path.basename(filename))[0]
            # extension = os.path.splitext(os.path.basename(filename))[1]

            # if extension.upper() != '.MP4':
            #     QMessageBox.information(self, "有問題", "檔案不是 MP4 喔!")
            # else:
            #     self.add_song(Song(" ", " ", " ", " ", basename, filename))

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
            QMessageBox.information(self, "Hello", "歌單空了喔!!")
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
            QMessageBox.information(self, '錯誤', '沒有歌曲再撥放喔!')

    def update_play_list_view(self):
        stringList: List[str] = []

        for song in self.playList:
            stringList.append(song.name + ", " + song.get_singers_name())

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
        for singer in song.singers:
            if self.singerEdit.text().upper() not in singer.name.upper():
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
        idLabel.setText("歌號:")
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
        langLabel.setText("語言:")
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
        singerTypeLabel.setText("歌手類型:")
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
        singerLabel.setText("歌手:")
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
        songNameLabel.setText("歌名:")
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
            stringList.append(song.name + ", " + song.get_singers_name())

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
        self.songNameLabel.setText(song.name)
        self.singerLabel.setText(song.get_singers_name())
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

        # hbox title and singer
        titleSingerWidget = QWidget()
        titleSingerHbox = QHBoxLayout()
        titleSingerHbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        titleSingerHbox.setContentsMargins(0, 0, 0, 0)
        titleSingerWidget.setFixedHeight(40)
        titleSingerWidget.setContentsMargins(0, 0, 0, 0)
        titleSingerWidget.setLayout(titleSingerHbox)

        self.songNameLabel = QLabel("歌名")
        self.singerLabel = QLabel('歌手')

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("QLabel{font-size: 18pt;}\n\
                        QListView{font-size: 18pt;}\n\
                        QButton{font-size: 18pt;}")
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())
