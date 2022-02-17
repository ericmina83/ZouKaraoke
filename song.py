from distutils.log import ERROR
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
    def __init__(self, name, singerId, singerType):
        self.singerId: int = singerId
        self.name: str = name
        self.songs: list[Song] = []
        self.singerType: SingerType = singerType


class SongVersion():
    def __init__(self, song, name):
        self.song: Song = song
        self.songpath = str
        self.name = name


class Song():

    def __init__(self, sn: str, songId: int, singers: list[Singer], name: str, lang: LangType, singerType: SingerType):
        self.sn = sn
        self.name = name
        self.songId = songId
        self.singers = singers
        self.lang = lang
        self.versions: list[SongVersion] = []
        self.singerType = singerType

    def get_singers_name(self):
        result = self.singers[0].name
        for i in range(1, len(self.singers)):
            result += '&' + self.singers[i].name
        return result

    def output_csv(self):
        return self.id + "," + langTypes[self.lang] + "," + self.name + "," + self.get_singers_name() + ',' + singerTypes[self.singerType] + "," + self.path


songs: List[Song] = []
singers: List[Singer] = []
versions: list[SongVersion] = []
singerType_singerId_singer: dict[SingerType, dict[int, Singer]] = {}
singerType_maxSingerId: dict[SingerType, int] = {}
lang_targetSingers_id_song: dict[LangType, dict[str, dict[int, Song]]] = {}
targetSingers_maxSongId: dict[str, int] = {}


def check_filename(basename: str, extension: str) -> SongVersion | None:

    if extension.upper() != ".mp4".upper():
        print("%s is not mp4" % basename)
        return None

    strs = basename.split("_")

    if len(strs) < 4:
        print("%s format isn't correct" % basename)
        return None

    # recognize id
    if idMatch.match(strs[0]) is None:
        print("%s id: %s is not ok" % basename, strs[0])
        return None  # if id can't be recognized, we will return give up this file

    sn = strs[0]
    langType = LangType(sn[0])
    singerType = SingerType(int(sn[1]))
    singerId = int(sn[2: 5])
    songId = int(sn[6: 8])

    # recognize singers' name
    singerNames = strs[2].replace('_', '').split('&')
    targetSingers: List[Singer] = []

    for singerName in singerNames:
        singerAlreadyExists = False  # a flag record this singer data created or not

        # get singer with same name and don't care the SingerType and singerId
        singer = next((tmpSinger for tmpSinger in singers if singerName.upper(
        ) in tmpSinger.name.upper() or tmpSinger.name.upper() in singerName.upper()), None)

        if (singer != None):
            singerAlreadyExists = True
        else:
            singer = singerType_singerId_singer[singerType].get(singerId)

            if (singer != None):  # if there is a singer we want, do nothing
                if (singer.name != singerName):  # but names of two are different
                    # we will create a new singer because the name is diffrent from original one
                    singerType_maxSingerId[singerType] += 1
                    singerId = singerType_maxSingerId[singerType]
                    singer = Singer(singerName, singerId, singerType)
                else:  # if the singer which already created
                    singerAlreadyExists = True
            else:  # if there is no singer we are finding, create a new singer
                singer = Singer(singerName, singerId, singerType)

        targetSingers.append(singer)

        if (singerAlreadyExists == False):
            singers.append(singer)
            singerType_singerId_singer[singerType][singerId] = singer

    targetSingers.sort(key=lambda singer: singer.singerId)

    # recognize language
    langStr = strs[1]
    if langMatch.match(langStr) is None:  # if lang format is not ok
        # we will use id's lang
        print("%s lang format is not ok" % basename)
    elif (langTypes[langType] != langStr):  # if lang
        print("%s lang is not match to id" % basename)
        langType = next(
            langType for langType in langTypes if langTypes[langType] == strs[1])

    # recognize song's name
    songName = strs[3]
    songAlreadyExists = False  # a flag record this singer data created or not

    targetSingersStr = str(targetSingers)

    id_song = lang_targetSingers_id_song[langType].get(targetSingersStr)

    song = None

    if (id_song == None):
        lang_targetSingers_id_song[langType][targetSingersStr] = {}

        song = next((tmpSong for tmpSong in songs if songName.upper() in tmpSong.name.upper(
        ) or singer.name.upper() in songName.upper()), None)

        if (song == None):
            if targetSingers_maxSongId.get(targetSingersStr) == None:
                targetSingers_maxSongId[targetSingersStr] = 0
            else:
                targetSingers_maxSongId[targetSingersStr] += 1

            song = Song(
                sn, targetSingers_maxSongId[targetSingersStr], targetSingers, songName, langType, singerType)
        else:
            songAlreadyExists = True
    else:
        song = id_song.get(songId)

        if (song == None):
            song = Song(sn, songId, targetSingers,
                        songName, langType, singerType)
        songAlreadyExists = True

    songs.append(song)

    if(songAlreadyExists == False):
        lang_targetSingers_id_song[langType][targetSingersStr][songId] = song

    version = SongVersion(song, songName)

    if(song == None):
        print('song is none')

    song.versions.append(version)
    versions.append(version)

    return version


def list_all_songs(path):
    path = os.path.abspath(path)
    print("Songs abspath: %s" % path)

    # initialization
    lang_targetSingers_id_song.clear()
    for langType in LangType:
        lang_targetSingers_id_song[langType] = {}

    singerType_maxSingerId.clear()
    for singerType in SingerType:
        singerType_maxSingerId[singerType] = 0

    singerType_singerId_singer.clear()
    for singerType in SingerType:
        singerType_singerId_singer[singerType] = {}

    targetSingers_maxSongId.clear()

    # iteration start
    for (dirpath, dirnames, filenames) in os.walk(path):

        for filename in filenames:
            songpath = os.path.join(dirpath, filename)

            basename = os.path.splitext(filename)[0]
            extension = os.path.splitext(filename)[1]

            version = check_filename(basename, extension)

            if version is None:
                continue
            else:
                version.songpath = songpath

        break  # do 1 time for iterate 1 layer (level)

    # log
    for song in songs:
        print(song.name)

    for singer in singers:
        print(singer.name)

    return songs, singers


def output_csv(songs):
    outF = open("myOutFile.csv", "w", encoding='utf8')

    for song in songs:
        outF.write(song.output_csv())
        outF.write("\n")

    outF.close()
