from PyQt5.QtWidgets import QWidget, QListView, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QLineEdit, QLabel
from PyQt5.QtCore import QStringListModel
from ReadSongs import *
import sys


class SearchListWidget(QWidget):
    def __init__(self, mainWindow):
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
        if self.singerEdit.text() not in song.singer:
            return False

        if self.songNameEdit.text() not in song.name:
            return False

        return True

    def on_edit_text_changed(self, str):
        self.searchList = list(
            filter(self.check_song_correct_or_not, self.mainWindow.songs))

        self.update_search_list_view()

    def create_column2(self):
        # VBox
        vbox = QVBoxLayout()

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
        vbox.addWidget(self.searchListView)

        # select button
        self.selectBtn = QPushButton("點歌")
        self.selectBtn.clicked.connect(self.on_select_btn_clicked)
        vbox.addWidget(self.selectBtn)

        return vbox

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
