from PyQt5.QtWidgets import QApplication, QWidget, QListView, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QFileDialog
from ReadSongs import *
from PyPlayer import PlayerWindow
import PlayListWidget
import SearchListWidget
import sys


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.playerWindow = PlayerWindow()

        self.get_songs_path_from_input_dialog()

        # hbox (parent)
        hbox = QHBoxLayout()

        # column 1: play list widget
        self.playListWidget = PlayListWidget.PlayListWidget(self)
        hbox.addWidget(self.playListWidget)

        # column 2: searching list Widget
        self.searchListWidget = SearchListWidget.SearchListWidget(self)
        hbox.addWidget(self.searchListWidget)

        # set parent layout
        self.setLayout(hbox)

    def print_songs(self):
        print('---------')
        for song in self.songs:
            print(song.name)

    def print_play_list(self):
        print('---------')
        for song in self.playList:
            print(song.name)

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
