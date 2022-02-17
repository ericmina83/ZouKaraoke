from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QWidget, QFileDialog, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QListView, QAbstractItemView
from typing import List
from song import *
from PyPlayer import PlayerWindow


class PlayListWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.playerWindow = PlayerWindow(self.next_song)
        self.playerWindow.show()
        self.selectedSongIndex = -1

        self.playList: list[SongVersion] = []  # songs will be played

        # column 1
        column1 = QVBoxLayout()

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

    def add_song(self, songVersion: SongVersion):

        if self.playerWindow.is_playing() is False and not self.playList:
            self.playerWindow.load_and_play_video(songVersion)
        else:
            self.playList.append(songVersion)
            self.update_play_list_view()

    def next_song(self):
        if self.playList:
            print("next song")
            song = self.playList[0]
            del self.playList[0]
            self.playerWindow.load_and_play_video(song)
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

        for songVersion in self.playList:
            stringList.append(songVersion.name + ", " +
                              songVersion.song.get_singers_name())

        model: QStringListModel = self.playListView.model()

        model.setStringList(stringList)

    def close_player(self):
        self.playerWindow.close()
