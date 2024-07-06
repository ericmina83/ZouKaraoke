from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QWidget, QFileDialog, QHBoxLayout, QAction, QMessageBox

from ZouKaraoke.Song import *
from ZouKaraoke.Container import Container
from ZouKaraoke.MainWindow.PlayListWidget import PlayListWidget
from ZouKaraoke.MainWindow.SearchListWidget import SearchListWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.container = Container()

        self.get_songs_path_from_input_dialog()

        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)

        # hBox (parent)
        hBox = QHBoxLayout()

        # column 1: play list widget
        self.playListWidget = PlayListWidget(self.container)
        hBox.addWidget(self.playListWidget)

        # column 2: searching list Widget
        self.searchListWidget = SearchListWidget(self.container)
        hBox.addWidget(self.searchListWidget)

        # set parent layout
        self.setLayout(hBox)

    def get_songs_path_from_input_dialog(self):

        list_all_songs(QFileDialog.getExistingDirectory(self, "請選擇歌庫路徑"))

        # for singer in self.singers:
        #     print(singer.name)
        #     for song in singer.songs:
        #         print("    " + song.name)
        output_csv(self.container.songs)

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
