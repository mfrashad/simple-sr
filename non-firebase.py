import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import textwrap

import subprocess
import speech_recognition as sr

r = sr.Recognizer()

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# Beaglebone Black pin configuration:
# RST = 'P9_12'
# Note the following are only used with SPI:
# DC = 'P9_15'
# SPI_PORT = 1
# SPI_DEVICE = 0

# 128x32 display with hardware I2C:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Note you can change the I2C address by passing an i2c_address parameter like:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

wrapper = textwrap.TextWrapper(width=20)


# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('Minecraftia.ttf', 16)

def clear(draw):
    draw.rectangle((0,0,width,height), outline=0, fill=0)


def print_oled(draw, disp, text, y=10):
    word_list = wrapper.wrap(text=text)
    for i in range(len(word_list)):
        draw.text((x, top+y+(i*8)), str(word_list[i]), font=font, fill=255)
    disp.image(image)
    disp.display()
    print(text)

last_text = ""

while True:

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        clear(draw)
        print_oled(draw, disp, "Say something!")
        print_oled(draw, disp, last_text, y=24)
        audio = r.listen(source, timeout=5)
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        clear(draw)
        print_oled(draw, disp, 'processing')
        last_text = r.recognize_google(audio, language='ms-MY')
        print_oled(draw, disp, last_text, y=24)
    except sr.UnknownValueError:
        print_oled(draw, disp, "Google Speech Recognition could not understand audio", y=20)
    except sr.RequestError as e:
        print_oled(draw, disp, "Could not request results from Google Speech Recognition service; {0}".format(e), y=20)

    # draw.text((x, top),       "IP: " + str(IP),  font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(.1)

