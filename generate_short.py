"""
generate_short.py
Creates a ~15-60s YouTube Short from a text prompt:
- Generates TTS audio (gTTS)
- Uses 1-3 stock images, adds caption text
- Exports a vertical 1080x1920 MP4
"""

import os
import random
import textwrap
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, TextClip
)
from gtts import gTTS
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

STOCK_DIR = os.getenv("STOCK_IMAGES_DIR", "./assets/images")
MUSIC = os.getenv("BACKGROUND_MUSIC", "./assets/music/background_loop.mp3")
OUT_DIR = os.getenv("OUTPUT_DIR", "./output")

# Video config
WIDTH, HEIGHT = 1080, 1920
FPS = 24
TARGET_DURATION = 20  # seconds, adjust for your short

os.makedirs(OUT_DIR, exist_ok=True)

def choose_images(n=2):
    imgs = [os.path.join(STOCK_DIR, f) for f in os.listdir(STOCK_DIR)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    if not imgs:
        raise FileNotFoundError("No stock images found in " + STOCK_DIR)
    return random.sample(imgs, min(n, len(imgs)))

def make_tts(text, out_path):
    tts = gTTS(text=text, lang="en")
    tts.save(out_path)
    return out_path

def wrap_caption(text, width=20):
    return "\n".join(textwrap.wrap(text, width=width))

def build_video_from_prompt(prompt, out_filename=None):
    # Basic prompt processing — you can replace with GPT generation
    captions = split_into_captions(prompt)
    images = choose_images(n=len(captions))
    
    audio_path = os.path.join(OUT_DIR, "tts.mp3")
    make_tts(prompt, audio_path)
    audio_clip = AudioFileClip(audio_path)
    audio_duration = min(audio_clip.duration, TARGET_DURATION)
    
    per_clip_duration = audio_duration / len(captions)
    clips = []
    for i, caption in enumerate(captions):
        img = images[i % len(images)]
        # Resize/or letterbox image to 1080x1920 preserving aspect
        clip = ImageClip(img).resize(height=HEIGHT)  # maintain aspect by height
        # If width less than needed, place on background
        if clip.w < WIDTH:
            bg = ImageClip(color=(0,0,0), size=(WIDTH, HEIGHT)).set_duration(per_clip_duration)
            clip = clip.set_position(("center","center"))
            comp = CompositeVideoClip([bg, clip.set_duration(per_clip_duration)])
        else:
            clip = clip.resize(width=WIDTH).set_duration(per_clip_duration)
            comp = clip.set_position(("center","center")).set_duration(per_clip_duration)
        
        # Add caption text
        wrapped = wrap_caption(caption, width=18)
        txt = TextClip(wrapped, fontsize=56, font="Arial-Bold", method="caption", size=(int(WIDTH*0.9), None))
        txt = txt.set_position(("center", int(HEIGHT*0.72))).set_duration(per_clip_duration).margin(bottom=20)
        comp = CompositeVideoClip([comp, txt]).set_duration(per_clip_duration)
        clips.append(comp)

    final = concatenate_videoclips(clips, method="compose")
    # Add background music (looped)
    if os.path.exists(MUSIC):
        bg = AudioFileClip(MUSIC).fx(lambda a: a.volumex(0.12))
        # loop or cut to match
        bg = bg.audio_loop(duration=audio_duration)
        final_audio = CompositeAudioClip([bg.set_start(0), audio_clip.set_start(0)])
        final = final.set_audio(final_audio)
    else:
        final = final.set_audio(audio_clip)

    final = final.set_fps(FPS).resize((WIDTH, HEIGHT))
    out_filename = out_filename or os.path.join(OUT_DIR, f"short_{int(random.random()*1e9)}.mp4")
    final.write_videofile(out_filename, codec="libx264", audio_codec="aac", threads=4, fps=FPS)
    return out_filename

def split_into_captions(prompt, max_captions=3):
    # naive split: break prompt into sentences or chunks
    sentences = [s.strip() for s in prompt.replace("?", ".").split(".") if s.strip()]
    if not sentences:
        return [prompt]
    # Limit to max_captions
    if len(sentences) > max_captions:
        # combine to fit
        joined = ". ".join(sentences)
        # split roughly into max_captions chunks
        chunk_size = max(1, len(joined)//max_captions)
        return [joined[i:i+chunk_size].strip() for i in range(0, len(joined), chunk_size)][:max_captions]
    return sentences

if _name_ == "_main_":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python generate_short.py \"Your prompt or script here\"")
        sys.exit(1)
    prompt = sys.argv[1]
    out = build_video_from_prompt(prompt)
    print("Generated:", out)
