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
MUSIC = os.getenv("BACKGROUND_MUSIC","./assets/music
