from PyQt5.QtWidgets import QApplication, QWidget, QListView, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QFileDialog
from ReadSongs import *
from PyPlayer import PlayerWindow
from PyQt5.QtCore import QStringListModel
import PlayListWidget
import sys


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.playerWindow = PlayerWindow()

        self.get_songs_path_from_input_dialog()

        # column 1: play list widget
        self.playListWidget = PlayListWidget.PlayListWidget(self)

        # column 2
        self.songsListView = QListView()
        self.songsListView.setModel(QStringListModel())

        # total horizontal box
        hbox = QHBoxLayout()
        hbox.addWidget(self.playListWidget)

        self.setLayout(hbox)

    def print_songs(self):
        print('---------')
        for song in self.songs:
            print(song.songName)

    def print_play_list(self):
        print('---------')
        for song in self.playList:
            print(song.songName)

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
