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

logging.basicConfig(level=logging.INFO)


def truncate_text(text: str, font: ImageFont, max_width: int):
    '''
        truncate text if it exceeds max_width
    '''
    if font.getlength(text) <= max_width:
        return text  # Fits, no need to trim
    
    while font.getlength(text + "...") > max_width and len(text) > 0:
        text = text[:-1]  # Remove last character
    
    return text + "..."  # Add ellipsis


def save_image(image_url: str,image_path: str):
    ''' 
        Send a GET request to fetch the image
        and save it as cover_art.jpg
        
        Args:
            image_url: url of the thumbnail to download
        Returns:
            image_path: path where the image should be saved
    '''
    response = requests.get(image_url)
    # Check if the request was successful
    if response.status_code == 200:
        # Open the file in binary write mode and save the image
        with open(image_path, 'wb') as file:
            file.write(response.content)
        print(f"Image saved as {image_path}")
        return image_path
    else:
        print(f"Failed to retrieve the image. Status code: {response.status_code}")


def create_display_image(image_path: str,
                         spotify_code_path:str,
                         song_name: str, artist_name: str,
                         song_font_path: str,
                         artist_font_path: str):
    
    # resize image to only take top part of the display
    print(image_path)
    foreground_image = Image.open(image_path).resize((444, 474))
    foreground_image = ImageOps.expand(foreground_image, border=3, fill="white")

    background_image = Image.open(image_path).resize((800,800))
    # blur the background image
    background_image = background_image.filter(ImageFilter.GaussianBlur(20))

    # prepare spotify code image to fit 480 pixels widtheee
    spotify_code_image = Image.open(spotify_code_path)
    new_width = 480
    # Calculate new height while keeping aspect ratio
    aspect_ratio = spotify_code_image.height / spotify_code_image.width
    new_height = int(new_width * aspect_ratio)
    # Resize while maintaining proportions
    spotify_code_image = spotify_code_image.resize(
        (new_width, new_height), Image.Resampling.LANCZOS
        )

    # output image path
    output_image_path = os.path.join(os.path.dirname(image_path), "converted_cover_art.jpg")

    # Create base image (480x800)
    canvas = Image.new("RGB", (480, 800), "white")
    
    background_image_offset = int(240 - background_image.width/2)
    # paste background image
    canvas.paste(background_image, (background_image_offset, 0))
    
    # paste foreground image
    canvas.paste(foreground_image, (15, 50))
    canvas.paste(spotify_code_image,(0, 800-spotify_code_image.height))

    # Compute average color for text
    # in numpy array it is a normal array of pixels
    bottom_pixels = np.array(canvas)[50+foreground_image.height:800-spotify_code_image.height, :, :]
    avg_color = tuple(np.mean(bottom_pixels, axis=(0, 1)).astype(int))

    # Determine brightness and choose text color
    brightness = (0.299 * avg_color[0] + 0.587 * avg_color[1] + 0.114 * avg_color[2])
    text_color = "black" if brightness > 128 else "white"

    # Draw text on the gradient
    draw = ImageDraw.Draw(canvas)

    # setup font sizes
    song_font_size = 40
    artist_font_size = 20

    # Set up fonts
    song_font = ImageFont.truetype(song_font_path, song_font_size)  # Bold and bigger
    artist_font = ImageFont.truetype(artist_font_path, artist_font_size)  # Smaller font

    # truncate text to ... in case the name of song is too long
    song_name = truncate_text(song_name, song_font, 450)
    artist_name = truncate_text(artist_name, artist_font, 450)

    # Get text sizes for centering
    song_font_height = song_font_size
    song_font_width = draw.textlength(song_name, font=song_font)
    artist_font_height = artist_font_size
    artist_font_width = draw.textlength(artist_name, font=artist_font)
    
    
    # (0,0) is top left
    # (x is towards left)
    # (y is towards down)

    # Text positions
    text1_x = 20
    text1_y = 500 + 70  # Padding from the top of the colored area

    text2_x = 20
    text2_y = text1_y + song_font_height + 10  # 10px padding below first line

    # Draw text
    draw.text((text1_x, text1_y), song_name, font=song_font, fill=text_color)
    draw.text((text2_x, text2_y), artist_name, font=artist_font, fill=text_color)

    # Save output image
    canvas.save(output_image_path)
    print(f"Image saved as: {output_image_path}, Text Color: {text_color}")


prev_song_name = ''
while True:
    try:
        base_dir = os.path.dirname(__file__)
        song_info = getSongInfo.getSongInfo()
        curr_song_name= song_info[0]

        if prev_song_name == curr_song_name:
            logging.info('Song not changed!')
            continue

        logging.info("Refreshing Spod!")
        prev_song_name = curr_song_name
        
        # logging.info(song_info[1])
        # The URL of the image
        image_url = song_info[1]
        print(song_info[3])
        spotify_code_url = f"https://scannables.scdn.co/uri/plain/png/000000/white/480/{song_info[3]}"
        image_path = save_image(image_url, os.path.join(base_dir, 'data', 'cover_art.jpg'))
        spotify_code_path = save_image(spotify_code_url, os.path.join(base_dir, 'data', 'spotify_code.jpg'))
        create_display_image(image_path,
                             spotify_code_path,
                             song_info[0],
                             song_info[2],
                             'fonts/helvetica-compressed-5871d14b6903a.otf',
                             'fonts/Helvetica.ttf')
        
        # exit()
        
        epd = epd7in3f.EPD()
        logging.info("init and Clear")
        epd.init()
        
        # used for clearing the display
        # epd.Clear()
        
        # Image file
        image_file = os.path.join(base_dir, 'data', 'converted_cover_art.jpg')
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
        epd.display(epd.getbuffer(img))
        
        # logging.info("Clear...")
        # epd.Clear()
        
        
    except IOError as e:
        logging.error(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        logging.info("Goto Sleep...")
        epd.sleep()
        epd7in3f.epdconfig.module_exit(cleanup=True)
        exit()

