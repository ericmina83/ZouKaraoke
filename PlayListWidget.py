from PyQt5.QtWidgets import QWidget, QListView, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QFileDialog
from ReadSongs import *
from main import MainWindow
from PyQt5.QtCore import QStringListModel
import sys


class PlayListWidget(QWidget):
    def __init__(self, mainWindow: MainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        self.selectedSong = None

        self.playList = self.mainWindow.songs.copy()  # songs will be played

        # column 1, play list view
        self.playListView = QListView()
        self.playListView.setModel(QStringListModel())
        self.update_play_list_view()
        self.playListView.clicked.connect(self.on_song_item_selected)

        # column 1, button bar, insert button
        self.insertBtn = QPushButton("插播")
        self.insertBtn.clicked.connect(self.on_insert_btn_clicked)

        # column 1, button bar, remove button
        self.removeBtn = QPushButton("移除")
        self.removeBtn.clicked.connect(self.on_remove_btn_clicked)

        # column 1, button bar
        buttonBar = QHBoxLayout()
        buttonBar.addWidget(self.insertBtn)
        buttonBar.addWidget(self.removeBtn)

        # column 1
        column1 = QVBoxLayout()
        column1.addWidget(self.playListView)
        column1.addLayout(buttonBar)

        self.setLayout(column1)

    def on_song_item_selected(self, modelIndex):
        self.selectedSong = self.playList[modelIndex.row()]
        print(self.selectedSong.songName)

    def on_insert_btn_clicked(self):
        if self.selectedSong is None:
            QMessageBox.information(self, '錯誤', '請選擇歌曲後才能插播')
        else:
            self.playList.remove(self.selectedSong)
            self.playList.insert(0, self.selectedSong)
            self.selectedSong = None
            self.update_play_list_view()

    def on_remove_btn_clicked(self):
        if self.selectedSong is None:
            QMessageBox.information(self, '錯誤', '請選擇歌曲後才能移除')
        else:
            self.playList.remove(self.selectedSong)
            self.selectedSong = None
            self.update_play_list_view()

    def update_play_list_view(self):
        stringList = []

        for song in self.playList:
            stringList.append(song.songName)

        self.playListView.model().setStringList(stringList)
