from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QWidget, QListView, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox
from ReadSongs import *
from PyPlayer import PlayerWindow


class PlayListWidget(QWidget):
    def __init__(self, mainWindow):
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

        self.setLayout(column1)

        self.update_play_list_view()

    def add_song(self, song: Song):

        if self.playerWindow.playing is False and not self.playList:
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
        if self.selectedSongIndex is -1:
            QMessageBox.information(self, '錯誤', '請選擇歌曲後才能插播')
        else:
            song = self.playList[self.selectedSongIndex]
            del self.playList[self.selectedSongIndex]
            self.playList.insert(0, song)
            self.selectedSongIndex = -1
            self.update_play_list_view()

    def on_remove_btn_clicked(self):
        if self.selectedSongIndex is -1:
            QMessageBox.information(self, '錯誤', '請選擇歌曲後才能移除')
        else:
            del self.playList[self.selectedSongIndex]
            self.selectedSongIndex = -1
            self.update_play_list_view()

    def update_play_list_view(self):
        stringList = []

        for song in self.playList:
            stringList.append(song.name)

        self.playListView.model().setStringList(stringList)

    def close_player(self):
        self.playerWindow.close()
