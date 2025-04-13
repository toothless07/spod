#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import numpy as np

import logging
from waveshare_epd import epd7in3f
import time
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import traceback
import color_epd_converter
from spotify_data import getSongInfo
import requests
from utils import *
import random
import datetime


logging.basicConfig(level=logging.INFO)

class Spod:
    def __init__(self, *args, **kwargs):
        self.epd = epd7in3f.EPD()
        logging.info("init and Clear")
        self.epd.init()
        self.prev_song_name = ''
        self.base_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.spotify_sync_spod = True
        self.picture_sync_spod = True

    def picture_sync(self):
        '''
            Use the display as a photo frame
            Sync the picture saved in ~/Pictures
        '''

        # exit early if picture sync is set to false
        if not self.picture_sync_spod:
            return False

        # Path to your Pictures directory
        pictures_dir = os.path.expanduser("~/Pictures")

        # Get all image files in the directory
        image_files = [f for f in os.listdir(pictures_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

        # Pick a random image file
        if image_files:
            random_image_path = os.path.join(pictures_dir, random.choice(image_files))
            img = Image.open(random_image_path)


        # force open a specific image
        img = Image.open('/home/toothless/Pictures/IMG2.JPG').convert("RGB")
        img = color_epd_converter.convert(img,
                                        orientation="portrait",
                                        width=480,
                                        height=800,
                                        crop_image=False,
                                        crop_x1=0,
                                        crop_y1=0,
                                        crop_x2=480,
                                        crop_y2=800,
                                        smart_crop = True)

        self.epd.display(self.epd.getbuffer(img))
        return True

    def spotify_sync(self):
        '''
            Sync the display with the cover art of currently playing song
        '''
        
        if not self.spotify_sync_spod:
            return False
        try:
            song_info = getSongInfo.getSongInfo()
            if not song_info:
                logging.info('Nothing playing!!')
                self.prev_song_name = ''
                return False
            self.curr_song_name = song_info[0]

            if self.prev_song_name == self.curr_song_name:
                logging.info('Song not changed!')
                return True

            # song changed
            self.prev_song_name = self.curr_song_name

            logging.info("Refreshing Spod!")

            # logging.info(song_info[1])
            # The URL of the image
            image_url = song_info[1]
            print(song_info[3])
            spotify_code_url = f"https://scannables.scdn.co/uri/plain/png/000000/white/480/{song_info[3]}"
            image_path = save_image(image_url, os.path.join(self.data_dir, 'cover_art.jpg'))
            spotify_code_path = save_image(spotify_code_url, os.path.join(self.data_dir, 'spotify_code.jpg'))
            create_spotify_display_image(image_path,
                                spotify_code_path,
                                song_info[0],
                                song_info[2],
                                'fonts/helvetica-compressed-5871d14b6903a.otf',
                                'fonts/Helvetica.ttf')

            # exit()
            # used for clearing the display
            # epd.Clear()

            # Image file
            image_file = os.path.join(self.data_dir, 'converted_cover_art.jpg')
            logging.info(f"Picking {image_file} for displaying")

            # Converting image into bmp format for displaying
            img = Image.open(image_file).convert("RGB")
            print(img.size)
            # exit()
            img = color_epd_converter.convert(img,
                                            orientation="portrait",
                                            width=480,
                                            height=800,
                                            crop_image=False,
                                            crop_x1=0,
                                            crop_y1=0,
                                            crop_x2=480,
                                            crop_y2=800)
            # Or just use the defaults
            # img = color_epd_converter.convert(img)

            img.save(os.path.join(os.path.dirname(image_path), "./final_display_art.bmp"))
            logging.info("Displaying the converted image")
            self.epd.display(self.epd.getbuffer(img))

            return True

            # logging.info("Clear...")
            # epd.Clear()


        except IOError as e:
            logging.error(e)

        except KeyboardInterrupt:
            logging.info("ctrl + c:")
            logging.info("Goto Sleep...")
            self.epd.sleep()
            epd7in3f.epdconfig.module_exit(cleanup=True)
            exit()
        
    def main(self):

        while True:
            now = time.localtime()
            # Define the time range
            # start = time(23, 0)  # 11:00 PM
            # end = time(10, 0)    # 10:00 AM

            # Check if current time is in the range, handling overnight wrap-around
            if now.tm_hour >= 10 or now.tm_hour < 23:
                if not self.spotify_sync():
                    self.picture_sync()
                    self.picture_sync_spod = False
                else:
                    self.picture_sync_spod = True
                time.sleep(60)
            else:
                print("Time is outside the range.")
                if self.picture_sync():
                    self.picture_sync_spod = False
                time.sleep(60)

if __name__ == '__main__':
    Spod().main()
