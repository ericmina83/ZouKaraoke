import os
import re
from enum import Enum

idMatch = re.compile('^[a-j][1-8]\d{6}$')
langMatch = re.compile("^((國|台|粵|日|英|客|韓)語|兒歌|其他|原住民)$")


class Lang(Enum):
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


langs = {
    Lang.NONE: '不考慮',
    Lang.CHINESE: '國語',
    Lang.TAIWANESE: '台語',
    Lang.HK: '粵語',
    Lang.JAPANESE: '日語',
    Lang.ENGLISH: '英語',
    Lang.HAKKA: '客語',
    Lang.ORIGINAL: '原住民語',
    Lang.KOREAN: '韓語',
    Lang.CHILDREN: '兒歌',
    Lang.OTHER: '其他',
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
    def __init__(self, name, gender, singerType):
        self.name = name
        self.gender = gender
        self.singerType = singerType


class Song():
    def __init__(self, path, id, lang, singer, name):
        self.path = path
        self.name = name
        self.id = id
        self.lang = Lang(id[0])
        self.singer = singer
        self.singerType = SingerType(int(id[1]))

    def output_csv(self):
        return self.id + "," + langs[self.lang] + "," + self.name + "," + self.singer + ',' + singerTypes[self.singerType] + "," + self.path


def check_filename(basename, extension):

    if extension != ".mp4":
        print("%s is not mp4" % basename)
        return False

    strs = basename.split("_")

    if len(strs) < 4:
        print("%s format isn't correct" % basename)
        return False

    if idMatch.match(strs[0]) is None:
        print("%s id is not ok" % basename)
        return False

    if langMatch.match(strs[1]) is None:
        print("%s lang is not ok" % basename)
        return False

    return True


def list_all_songs(path):
    path = os.path.abspath(path)
    print("Songs abspath: %s" % path)

    songs = []

    for (dirpath, dirnames, filenames) in os.walk(path):

        for filename in filenames:
            songpath = os.path.join(dirpath, filename)
            print("songpath is %s" % songpath)

            basename = os.path.splitext(filename)[0]
            extension = os.path.splitext(filename)[1]

            if check_filename(basename, extension) is False:
                continue

            strs = basename.split("_")

            songs.append(Song(songpath, strs[0], strs[1], strs[2], strs[3]))

        break  # do 1 time for iterate 1 layer (level)

    return songs


def output_csv(songs):
    outF = open("myOutFile.csv", "w", encoding='utf8')

    for song in songs:
        outF.write(song.output_csv())
        outF.write("\n")

    outF.close()
