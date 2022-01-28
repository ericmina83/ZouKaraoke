import re
from cProfile import label
from glob import glob
from multiprocessing import Condition
from xml.etree.ElementTree import tostring
import threading
from moviepy.editor import *
from moviepy.audio.fx.volumex import *
from os import walk
import tkinter as tk
import pygame

movie_playing = False
end_app = False
searchText = None
cv = Condition()
path = "./Songs"


def play_video():
    global cv
    global movie_playing
    while True:
        cv.acquire()
        cv.wait_for(lambda: movie_playing)
        cv.release()

        if end_app is True:
            break

        clip = VideoFileClip('./Songs/YOASOBI「夜に駆ける」 Official Music Video.mp4')
        clip.preview()

        clip.close()

        print("song end")

        pygame.display.quit()

        movie_playing = False


t = threading.Thread(target=play_video)
t.start()


def play_video_thread():
    global movie_playing
    if movie_playing == False:
        movie_playing = True
        cv.acquire()
        cv.notify()
        cv.release()


window = tk.Tk()
window.title('window')
window.geometry('500x100')


def list_all_files():
    f = []
    for (dirpath, dirnames, filenames) in walk(path):
        f.extend(filenames)
        break
    print(f)
    global searchText
    print(searchText)


def initialize(window):
    playButton = tk.Button(window, text="play", command=play_video_thread)
    playButton.pack()

    listButton = tk.Button(window, text="list",
                           command=list_all_files)
    listButton.pack()

    global searchText
    searchText = tk.StringVar()
    searchBar = tk.Entry(window, textvariable=searchText,
                         validate='key', validatecommand=lambda: print("XX"))
    searchBar.pack()


initialize(window)

window.mainloop()

end_app = movie_playing = True

cv.acquire()
cv.notify()
cv.release()

t.join()

print("app end")
# pygame.quit()
