from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QWidget, QFileDialog, QHBoxLayout, QAction, QMessageBox
from song import *

from playlistwidget import PlayListWidget
from searchlistwidget import SearchListWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.songs: List[Song] = []
        self.singers: List[Singer] = []

        self.get_songs_path_from_input_dialog()

        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)

        # hbox (parent)
        hbox = QHBoxLayout()

        # column 1: play list widget
        self.playListWidget = PlayListWidget()
        hbox.addWidget(self.playListWidget)

        # column 2: searching list Widget
        self.searchListWidget = SearchListWidget(self.playListWidget.add_song)
        hbox.addWidget(self.searchListWidget)

        # set parent layout
        self.setLayout(hbox)

    def get_songs_path_from_input_dialog(self):

        list_all_songs(QFileDialog.getExistingDirectory(
            self, "請選擇歌庫路徑"))

        # for singer in self.singers:
        #     print(singer.name)
        #     for song in singer.songs:
        #         print("    " + song.name)
        output_csv(self.songs)

    def closeEvent(self, event: QEvent):
        close = QMessageBox()
        close.setText("你確定要離開嗎?")
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        close = close.exec()

        if close == QMessageBox.Yes:
            event.accept()
            self.playListWidget.close_player()
        else:
            event.ignore()
