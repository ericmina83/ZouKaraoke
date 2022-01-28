import os
import re

idMatch = re.compile('^[a-j][1-8]\d{6}$')
langMatch = re.compile("^((國|台|粵|日|英|客|韓)語|兒歌|其他|原住民)$")


class Singer():
    def __init__(self, name, gender):
        self.name = name
        self.gender = gender


class Song():
    def __init__(self, path, id, lang, singer, name):
        self.path = path
        self.name = name
        self.id = id
        self.lang = lang
        self.singer = singer

        if id[0] == 'a':
            print('國語')

    def output_csv(self):
        return self.id + "," + self.lang + "," + self.name + "," + self.singer + "," + self.path


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
