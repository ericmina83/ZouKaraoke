from enum import Enum
import re
import os
import re
from typing import List

idMatch = re.compile('^[a-j][0-8]\d{6}$')
langMatch = re.compile("^((國|台|粵|日|英|客|韓)語|兒歌|其他|原住民)$")


class LangType(Enum):
    NONE = ' '
    CHINESE = 'a'
    TAIWANESE = 'b'
    HK = 'c'
    JAPANESE = 'd'
    ENGLISH = 'e'
    HAKKA = 'f'
    ORIGINAL = 'g'
    KOREAN = 'h'
    CHILDREN = 'i'
    OTHER = 'j'


class SongType(Enum):
    NONE = '無'
    ORIGINAL = '原唱'
    COMPANY = '伴唱'
    LEFT_RIGHT_OLD = ''
    LEFT_RIGHT = '人樂分離'


class SingerType(Enum):
    NONE = 0
    FEMALE = 1
    MALE = 2
    GROUP = 3
    TOGATHER = 4
    FOREIGN_FEMALE = 5
    FOREIGN_MALE = 6
    FOREIGN_GROUP = 7
    OTHER = 8


langTypes = {
    LangType.NONE: '不考慮',
    LangType.CHINESE: '國語',
    LangType.TAIWANESE: '台語',
    LangType.HK: '粵語',
    LangType.JAPANESE: '日語',
    LangType.ENGLISH: '英語',
    LangType.HAKKA: '客語',
    LangType.ORIGINAL: '原住民語',
    LangType.KOREAN: '韓語',
    LangType.CHILDREN: '兒歌',
    LangType.OTHER: '其他',
}

singerTypes = {
    SingerType.NONE: "不考慮",
    SingerType.FEMALE: "國語女歌手",
    SingerType.MALE: "國語男歌手",
    SingerType.GROUP: "國語團體",
    SingerType.TOGATHER: "合唱",
    SingerType.FOREIGN_FEMALE: "外語女歌手",
    SingerType.FOREIGN_MALE: "外語男歌手",
    SingerType.FOREIGN_GROUP: "外語團體",
    SingerType.OTHER: "其他",
}


class Singer():
    def __init__(self, name):
        self.name: str = name
        self.songs: list[Song] = []


class Song():

    path: str
    name: str
    n_id: str
    lang: LangType
    singerType: SingerType

    def __init__(self, path, id, lang, singer: Singer, name, song_original_path):

        if song_original_path is None:
            self.path: str = path
            self.name: str = name
            self.id: str = id
            self.lang: LangType = LangType(id[0])
            self.singers: List[Singer] = singer
            self.singerType = SingerType(int(id[1]))
        else:
            self.name: str = name
            self.id: str = ""
            self.lang: LangType = LangType.NONE
            self.singers: List[Singer] = Singer("")
            self.singerType = SingerType.NONE
            self.path = song_original_path

    def get_singers_name(self):
        result = self.singers[0].name
        for i in range(1, len(self.singers)):
            result += '&' + self.singers[i].name
        return result

    def output_csv(self):
        return self.id + "," + langTypes[self.lang] + "," + self.name + "," + self.get_singers_name() + ',' + singerTypes[self.singerType] + "," + self.path


def check_filename(basename: str, extension: str):

    if extension.upper() != ".mp4".upper():
        print("%s is not mp4" % basename)
        return False

    strs = basename.split("_")

    if len(strs) < 4:
        print("%s format isn't correct" % basename)
        return False

    if idMatch.match(strs[0]) is None:
        print("%s id: %s is not ok" % basename, strs[0])
        return False

    if langMatch.match(strs[1]) is None:
        print("%s lang is not ok" % basename)
        return False

    return True


def list_all_songs(path):
    path = os.path.abspath(path)
    print("Songs abspath: %s" % path)

    songs: List[Song] = []
    singers: List[Singer] = []

    for (dirpath, dirnames, filenames) in os.walk(path):

        for filename in filenames:
            songpath = os.path.join(dirpath, filename)

            basename = os.path.splitext(filename)[0]
            extension = os.path.splitext(filename)[1]

            if check_filename(basename, extension) is False:
                continue

            strs = basename.split("_")

            singerStrs = strs[2].replace(' ', '').replace('_', '').split('&')

            targetSinger: List[Singer] = []

            for singerStr in singerStrs:
                if len(singers) == 0:
                    singer = Singer(singerStr)
                    singers.append(singer)
                else:
                    singer = next(
                        (singer for singer in singers if singerStr in singer.name or singer.name in singerStr),
                        None)

                    if singer is None:
                        singer = Singer(singerStr)
                        singers.append(singer)

                targetSinger.append(singer)

            try:
                song = Song(songpath, strs[0], strs[1],
                            targetSinger, strs[3], None)
                songs.append(song)

                for singer in targetSinger:
                    singer.songs.append(song)
            except ValueError:
                print("song %s value error!" % basename)

        break  # do 1 time for iterate 1 layer (level)

    return songs, singers
