from PyQt5.QtWidgets import QApplication, QWidget, QListView, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QFileDialog
from ReadSongs import *
from PyPlayer import PlayerWindow
from PyQt5.QtCore import QStringListModel
import sys


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.playerWindow = PlayerWindow()

        self.get_songs_path_from_input_dialog()
        self.playList = self.songs.copy()  # songs will be played
        self.selectedPlayListSong = None

        # column 1, play list view
        self.playListView = QListView()
        self.playListView.setModel(QStringListModel())
        self.update_play_list_view()
        self.playListView.clicked.connect(self.play_list_view_selected)

        # column 1, button bar, insert button
        self.insertBtn = QPushButton("插播")
        self.insertBtn.clicked.connect(self.on_play_list_insert_btn_clicked)

        # column 1, button bar, remove button
        self.removeBtn = QPushButton("移除")
        self.removeBtn.clicked.connect(self.on_play_list_remove_btn_clicked)

        # column 1, button bar
        buttonBar = QHBoxLayout()
        buttonBar.addWidget(self.insertBtn)
        buttonBar.addWidget(self.removeBtn)

        # column 1
        column1 = QVBoxLayout()
        column1.addWidget(self.playListView)
        column1.addLayout(buttonBar)

        # column 2
        self.songsListView = QListView()
        self.songsListView.setModel(QStringListModel())

        # total horizontal box
        hbox = QHBoxLayout()
        hbox.addLayout(column1)

        self.setLayout(hbox)

    def print_songs(self):
        print('---------')
        for song in self.songs:
            print(song.songName)

    def print_play_list(self):
        print('---------')
        for song in self.playList:
            print(song.songName)

    def on_play_list_insert_btn_clicked(self):
        if self.selectedPlayListSong is None:
            QMessageBox.information(self, '錯誤', '請選擇歌曲後才能插播')
        else:
            self.playList.remove(self.selectedPlayListSong)
            self.playList.insert(0, self.selectedPlayListSong)
            self.selectedPlayListSong = None
            self.update_play_list_view()

    def on_play_list_remove_btn_clicked(self):
        if self.selectedPlayListSong is None:
            QMessageBox.information(self, '錯誤', '請選擇歌曲後才能移除')
        else:
            self.playList.remove(self.selectedPlayListSong)
            self.selectedPlayListSong = None
            self.update_play_list_view()

    def play_list_view_selected(self, modelIndex):
        self.selectedPlayListSong = self.playList[modelIndex.row()]
        print(self.selectedPlayListSong.songName)

    def update_play_list_view(self):
        stringList = []

        for song in self.playList:
            stringList.append(song.songName)

        self.playListView.model().setStringList(stringList)

    def get_songs_path_from_input_dialog(self):
        songsPath = QFileDialog.getExistingDirectory(
            self, "請選擇歌庫路徑")

        self.songs = list_all_songs(songsPath)
        output_csv(self.songs)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())
