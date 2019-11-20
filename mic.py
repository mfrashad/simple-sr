import time

from datetime import datetime

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import subprocess
import speech_recognition as sr

## Firebase Setup

CRED_PATH = '/home/pi/serviceAccount.json'

# Use a service account
cred = credentials.Certificate(CRED_PATH)
firebase_admin.initialize_app(cred)

db = firestore.client()

## Speech Recognition Setup

r = sr.Recognizer()

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

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

language = 'en-US'
last_text = ""


# Load default font.
# font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('Minecraftia.ttf', 20)

def clear(draw):
    draw.rectangle((0,0,width,height), outline=0, fill=0)


def print_oled(draw, disp, text, y=10):
    draw.text((x, top+y), str(text), font=font, fill=255)
    disp.image(image)
    disp.display()
    print(text)

def save_message(db, message, lang='en-US', date=None, record=None):
    if date is None:
        date = datetime.now()
    data = {
        u'text': message,
        u'date': date,
        u'language': lang,
        u'record': record
    }
    db.collection(u'transcriptions').add(data)

def update_status(db, status):
    data = {
        u'status': status
    }
    db.collection(u'variables').document(u'status').set(data)

def on_change_language(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        global language
        lang_dict = doc.to_dict()
        language = lang_dict['value']
        print(u'Language: {}'.format(lang_dict['value']))


lang_ref = db.collection(u'settings').document(u'language')
lang_watch = lang_ref.on_snapshot(on_change_language)

while True:

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        clear(draw)
        update_status(db, 'Listening...')
        print_oled(draw, disp, "Say something!")
        print_oled(draw, disp, last_text, y=24)
        audio = r.listen(source)
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        clear(draw)
        print_oled(draw, disp, 'Processing...')
        update_status(db, 'Processing...')
        last_text = r.recognize_google(audio, language=language)
        print_oled(draw, disp, last_text, y=24)
        save_message(db, last_text)
    except sr.UnknownValueError:
        update_status(db, 'Unrecognized, try again!')
        print_oled(draw, disp, "Unrecognized, please say again!", y=20)
    except sr.RequestError as e:
        print_oled(draw, disp, "Connection error; {0}".format(e), y=20)

    # draw.text((x, top),       "IP: " + str(IP),  font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(.1)

