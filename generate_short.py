"""
generate_short.py
creates a - 15-60s Youtube Short from a text prompt:
-generates TTS audio (gTTS0
-Uses 1-3 stock images.adds caption text
-Export a vertical 1080*1920 MP4
"""

import os
import random
import textrap
from moviepy.editor import (
  ImageClip, AudioFileClip, CompositeVideoClip,concatenate_videoclips,Textclip
)
from gtts import gTTS
from dotenv import load_dotenv
from PIL import Images

load_dotenv()

STOCK_DIR = os.getenv("STOCK_IMAGES_DIR", "./assets/images")
MUSIC = os.getenv("BACKGROUND_MUSIC","./assets/music/background_loop.mp3")
OUT_DIR = os.getenv("OUTPUT_DIR","./output")

# Video config
WIDTH,HEIGHT = 1080, 1920
FPS = 24
TARGET_DURATION = 20 #secondss, adjust for your short

os.makedirs(OUT_DIR, exist_ok=True)

def choose_images(n=2):
  imgs = [os.path.join(STOCK_DIR, f) for f in os.listdir(STOCK_DIR)
          if f.lower().endswith((".jpg",".jpeg","png"))]
  if not imgs:
    raise FileNotFoundError("No stock images found in" + STOCK_DIR)
    return random.sample(imgs, min(n, lens(imgs)))

def make_tts(text, out_path):
  tts = gTTS(text=text, lang="en")
  tts.save(out_path)
  return out_path

def make_tts
