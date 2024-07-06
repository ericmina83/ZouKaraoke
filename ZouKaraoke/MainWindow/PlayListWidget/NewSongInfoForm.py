import difflib
from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QListView,
    QComboBox,
)
from typing import List

from ZouKaraoke.Song import *


def diff_two_strings(a: str, b: str) -> float:

    diff_count = 0

    for i, s in enumerate(difflib.ndiff(a, b)):
        if s[0] == " ":
            diff_count -= 5
        elif s[0] == "-":
            diff_count += 2
        elif s[0] == "+":
            diff_count += 1

    return diff_count


class NewSongInfoForm(QWidget):
    def __init__(self):
        super().__init__()

        self.singers: List[Singer] = []
        self.songs: List[Song] = []

        vboxTotal = QVBoxLayout()

        hboxTotal = QHBoxLayout()
        vboxTotal.addLayout(hboxTotal)

        # search song
        songNameSearchVbox = QVBoxLayout()

        # song language
        hboxSongLang = QHBoxLayout()

        hboxSongLang.addWidget(QLabel("語言"))

        self.songLangComboBox = QComboBox()
        self.songLangComboBox.addItems(list(map(lambda x: langTypes[x], LangType)))
        self.songLangComboBox.currentIndexChanged.connect(
            self.on_song_lang_index_changed
        )
        hboxSongLang.addWidget(self.songLangComboBox)

        songNameSearchVbox.addLayout(hboxSongLang)

        # song name
        hboxSongName = QHBoxLayout()

        hboxSongName.addWidget(QLabel("歌名"))

        self.songNameLineEdit = QLineEdit()
        self.songNameLineEdit.textChanged.connect(self.on_song_text_changed)
        hboxSongName.addWidget(self.songNameLineEdit)
        songNameSearchVbox.addLayout(hboxSongName)

        # song list view
        self.songNameListView = QListView()
        self.songNameListView.setModel(QStringListModel())
        self.songNameListView.clicked.connect(self.on_song_selected)
        songNameSearchVbox.addWidget(self.songNameListView)
        hboxTotal.addLayout(songNameSearchVbox)

        # search singer
        singerSearchVBox = QVBoxLayout()

        # singer type
        hboxSingerType = QHBoxLayout()

        hboxSingerType.addWidget(QLabel("歌手類型"))

        self.singerTypeComboBox = QComboBox()
        self.singerTypeComboBox.addItems(
            list(map(lambda singerType: singerTypes[singerType], SingerType))
        )
        self.singerTypeComboBox.currentIndexChanged.connect(
            self.on_singer_type_index_changed
        )
        hboxSingerType.addWidget(self.singerTypeComboBox)

        singerSearchVBox.addLayout(hboxSingerType)

        # singer list view
        hboxSinger = QHBoxLayout()
        self.singerLineEdit = QLineEdit()
        self.singerLineEdit.textChanged.connect(self.on_singer_text_changed)
        hboxSinger.addWidget(QLabel("歌手"))
        hboxSinger.addWidget(self.singerLineEdit)
        singerSearchVBox.addLayout(hboxSinger)

        self.singerlistview = QListView()
        self.singerlistview.setModel(QStringListModel())
        self.singerlistview.clicked.connect(self.on_singer_selected)
        singerSearchVBox.addWidget(self.singerlistview)
        hboxTotal.addLayout(singerSearchVBox)

        self.saveBtn = QPushButton()
        self.saveBtn.clicked.connect(self.on_save_clicked)
        vboxTotal.addWidget(self.saveBtn)

        self.setLayout(vboxTotal)

        self.update_songname_list_view()
        self.update_singer_list_view()

        # for singer in self.mainWindow.singers:
        #     print(singer.name)

    # song
    def check_song_correct_or_not(self, version: SongVersion):
        song = version.song
        for singer in song.singers:
            if self.singerLineEdit.text().upper() not in singer.name.upper():
                return False

        if self.songNameLineEdit.text().upper() not in song.name.upper():
            return False

        currentSingerType = list(SingerType)[self.singerTypeComboBox.currentIndex()]

        if (
            currentSingerType is not song.singerType
            and currentSingerType is not SingerType.NONE
        ):
            return False

        currentLang = list(LangType)[self.songLangComboBox.currentIndex()]

        if currentLang is not song.lang and currentLang is not LangType.NONE:
            return False

        return True

    def check_every_songs_correct_or_not(self):
        # self.songs = filter(lambda song: song.name.upper() in text.upper(
        # ) or text.upper() in song.name.upper(), self.mainWindow.songs)

        # self.songs = list(sorted(songs,
        # key=lambda song: diff_two_strings(song.name.upper(), text.upper())))

        self.songs = list(filter(self.check_song_correct_or_not, versions))

        self.update_songname_list_view()

    def update_songname_list_view(self):

        model: QStringListModel = self.songNameListView.model()
        model.setStringList(list(map(lambda song: song.name, self.songs)))

    def on_song_text_changed(self, text):
        self.check_every_songs_correct_or_not()

    def on_song_lang_index_changed(self, index):
        self.check_every_songs_correct_or_not()

    def on_song_selected(self, modelIndex):
        self.songNameLineEdit.setText(self.songs[modelIndex.row()].name)

    # singer
    def check_singer_correct_or_not(self, singer: Singer):

        if self.singerLineEdit.text().upper() not in singer.name.upper():
            return False

        currentSingerType = list(SingerType)[self.singerTypeComboBox.currentIndex()]

        if (
            currentSingerType is not singer.singerType
            and currentSingerType is not SingerType.NONE
        ):
            return False

        return True

    def check_every_singers_correct_or_not(self):
        # self.singers = list(filter(
        #     lambda singer: text in singer.name, self.mainWindow.singers))

        # self.singers = list(sorted(singers,
        #                            key=lambda singer: diff_two_strings(singer.name.upper(), text.upper())))

        self.singers = list(filter(self.check_singer_correct_or_not, singers))

        self.update_singer_list_view()

        self.check_every_songs_correct_or_not()

    def update_singer_list_view(self):
        model: QStringListModel = self.singerlistview.model()
        model.setStringList(list(map(lambda singer: singer.name, self.singers)))

    def on_singer_text_changed(self, text):

        self.check_every_singers_correct_or_not()

    def on_singer_type_index_changed(self, index):
        self.check_every_singers_correct_or_not()

    def on_singer_selected(self, modelIndex):
        self.singerLineEdit.setText(self.singers[modelIndex.row()].name)

    def on_save_clicked(self):
        print("haha")
