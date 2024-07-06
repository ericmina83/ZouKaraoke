from typing import List

from ZouKaraoke.Song import Song, Singer
from ZouKaraoke.EventBus import EventBus


class Container:
    def __init__(self):
        self.songs: List[Song] = []
        self.singers: List[Singer] = []
        self.eventBus = EventBus()
