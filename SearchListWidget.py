from PyQt5.QtWidgets import QWidget, QListView, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QLineEdit, QLabel, QComboBox
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
        if self.singerEdit.text().upper() not in song.singer.upper():
            return False

        if self.songNameEdit.text().upper() not in song.name.upper():
            return False

        currentSingerType = list(SingerType)[self.singerTypeBox.currentIndex()]

        if currentSingerType is not song.singerType and currentSingerType is not SingerType.NONE:
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

        self.singerTypeBox = QComboBox()
        self.singerTypeBox.addItems(
            list(map(lambda x: singerTypes[x], SingerType)))
        self.singerTypeBox.currentIndexChanged.connect(
            self.on_singer_type_box_index_changed)
        vbox.addWidget(self.singerTypeBox)

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
