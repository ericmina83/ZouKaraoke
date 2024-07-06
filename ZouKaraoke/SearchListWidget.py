from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox,
    QLabel,
    QListView,
    QComboBox,
    QAbstractItemView,
)
from typing import Callable, List

from ZouKaraoke.Song import *


class SearchListWidget(QWidget):
    searchList: list[SongVersion] = []
    selectedSongVersion: SongVersion = None
    add_song_to_play_list_callback: Callable[[Song], None]

    def __init__(self, add_song_to_play_list_callback: Callable[[SongVersion], None]):
        super().__init__()

        self.add_song_to_play_list_callback = add_song_to_play_list_callback
        self.searchList = versions.copy()

        # hbox (parent layout)
        hbox = QHBoxLayout()

        # column 2
        column2 = self.create_column2()
        hbox.addLayout(column2)

        # add parent layout
        self.setLayout(hbox)

        self.update_search_list_view()

    def check_song_correct_or_not(self, version: SongVersion):
        song = version.song
        for singer in song.singers:
            if self.singerEdit.text().upper() not in singer.name.upper():
                return False

        if self.songNameEdit.text().upper() not in song.name.upper():
            return False

        if self.snEdit.text().upper() not in song.sn.upper():
            return False

        currentSingerType = list(SingerType)[self.singerTypeBox.currentIndex()]

        if (
            currentSingerType is not song.singerType
            and currentSingerType is not SingerType.NONE
        ):
            return False

        currentLang = list(LangType)[self.langBox.currentIndex()]

        if currentLang is not song.lang and currentLang is not LangType.NONE:
            return False

        return True

    def check_every_songs_correct_or_not(self):
        self.searchList = list(filter(self.check_song_correct_or_not, versions))

        self.update_search_list_view()

    def on_edit_text_changed(self, str):
        self.check_every_songs_correct_or_not()

    def on_singer_type_box_index_changed(self, index):
        self.check_every_songs_correct_or_not()

    def create_column2(self):
        # VBox
        vbox = QVBoxLayout()

        # HBox id
        hboxId = QHBoxLayout()
        vbox.addLayout(hboxId)

        # HBox id, label
        idLabel = QLabel()
        idLabel.setText("歌號:")
        hboxId.addWidget(idLabel)

        # HBox id, Line edit
        self.snEdit = QLineEdit()
        self.snEdit.textChanged.connect(self.on_edit_text_changed)
        hboxId.addWidget(self.snEdit)

        # HBox lang
        hboxLang = QHBoxLayout()
        vbox.addLayout(hboxLang)

        # HBox lang, label
        langLabel = QLabel()
        langLabel.setText("語言:")
        hboxLang.addWidget(langLabel)

        # HBox lang, combobox
        self.langBox = QComboBox()
        self.langBox.addItems(list(map(lambda x: langTypes[x], LangType)))
        self.langBox.currentIndexChanged.connect(self.on_singer_type_box_index_changed)
        hboxLang.addWidget(self.langBox)

        # HBox singerType
        hboxSingerType = QHBoxLayout()
        vbox.addLayout(hboxSingerType)

        # HBox singerType, label
        singerTypeLabel = QLabel()
        singerTypeLabel.setText("歌手類型:")
        hboxSingerType.addWidget(singerTypeLabel)

        # HBox singerType, combobox
        self.singerTypeBox = QComboBox()
        self.singerTypeBox.addItems(list(map(lambda x: singerTypes[x], SingerType)))
        self.singerTypeBox.currentIndexChanged.connect(
            self.on_singer_type_box_index_changed
        )
        hboxSingerType.addWidget(self.singerTypeBox)

        # HBox singer
        hbox1 = QHBoxLayout()
        vbox.addLayout(hbox1)

        # HBox singer, label
        singerLabel = QLabel()
        singerLabel.setText("歌手:")
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
        songNameLabel.setText("歌名:")
        hbox2.addWidget(songNameLabel)

        # HBox song name, line edit
        self.songNameEdit = QLineEdit()
        self.songNameEdit.textChanged.connect(self.on_edit_text_changed)
        hbox2.addWidget(self.songNameEdit)

        # search list view
        self.searchListView = QListView()
        self.searchListView.setModel(QStringListModel())
        self.searchListView.clicked.connect(self.on_song_item_selected)
        self.searchListView.doubleClicked.connect(self.on_song_item_double_clicked)
        self.searchListView.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        vbox.addWidget(self.searchListView)

        # select button
        self.selectBtn = QPushButton("點歌")
        self.selectBtn.clicked.connect(self.on_select_btn_clicked)
        vbox.addWidget(self.selectBtn)

        return vbox

    def on_song_item_double_clicked(self, modelIndex):
        self.add_song_to_play_list_callback(self.searchList[modelIndex.row()])
        self.selectedSongVersion = None

    def on_song_item_selected(self, modelIndex):
        self.selectedSongVersion = self.searchList[modelIndex.row()]
        print(self.selectedSongVersion.song.name)

    def on_select_btn_clicked(self):
        if self.selectedSongVersion is None:
            QMessageBox.information(self, "錯誤", "請選擇歌曲後才能點歌")
        else:
            self.add_song_to_play_list_callback(self.selectedSongVersion)
            self.selectedSongVersion = None

    def update_search_list_view(self):
        stringList = []

        for songVersion in self.searchList:
            stringList.append(
                songVersion.name + ", " + songVersion.song.get_singers_name()
            )

        self.searchListView.model().setStringList(stringList)
