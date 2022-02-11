
import difflib
from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QLabel, QListView
from typing import List
from song import *


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


class NewSongInfoForm(QWidget):
    def __init__(self):
        super().__init__()

        self.singers: List[Singer] = []
        self.songs: List[Song] = []

        vboxTotal = QVBoxLayout()

        hboxTotal = QHBoxLayout()
        vboxTotal.addLayout(hboxTotal)

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

        self.saveBtn = QPushButton()
        self.saveBtn.clicked.connect(self.on_save_clicked)
        vboxTotal.addWidget(self.saveBtn)

        self.setLayout(vboxTotal)

        self.update_songname_list_view('')
        self.update_singer_list_view('')

        # for singer in self.mainWindow.singers:
        #     print(singer.name)

    def update_songname_list_view(self, text: str):
        # self.songs = filter(lambda song: song.name.upper() in text.upper(
        # ) or text.upper() in song.name.upper(), self.mainWindow.songs)

        self.songs = list(sorted(songs,
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
        print('haha')
