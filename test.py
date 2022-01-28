from glob import glob
from xml.etree.ElementTree import tostring
import threading
from moviepy.editor import *
from moviepy.audio.fx.volumex import *
from os import walk
import tkinter as tk
import pygame

while True:

    # pygame.display.set_caption('Hello World!')

    clip = VideoFileClip('./Songs/YOASOBI「夜に駆ける」 Official Music Video.mp4')
    clip.preview()

    clip.close()
    del clip

    # pygame.quit()
