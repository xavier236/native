"""
youtube_upload.py
Uploads a given video file to YouTube using OAuth2. Requires:
- client_secrets.json (from Google Cloud Console with YouTube Data API enabled)
- This script will create a token file after first run for offline refresh.
"""

import os
import pickle
import argparse
from dotenv import load_dotenv

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_OAUTH_CLIENT_SECRETS", "client_secrets.json")
TOKEN_FILE = os.getenv("YOUTUBE_CREDENTIALS_TOKEN", "yt_token.json")
CHANNEL_ID = os.getenv("CHANNEL_ID", None)
PRIVACY = os.getenv("DEFAULT_PRIVACY_STATUS", "public")

def get_authenticated_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        import json
        with open(TOKEN_FILE, "r") as fh:
            data = json.load(fh)
        # google-auth library expects Credentials object; simplest approach is to do a fresh flow if token missing or expired
        # For brevity we'll run InstalledAppFlow each time if token not valid
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    creds = flow.run_console()
    return build("youtube", "v3", credentials=creds)

def upload_video(youtube, file, title, description="", tags=None, categoryId="22", privacyStatus=PRIVACY):
    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags or [],
            "categoryId": categoryId
        },
        "status": {
            "privacyStatus": privacyStatus
        }
    }
    media = MediaFileUpload(file, chunksize=-1, resumable=True, mimetype="video/*")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")
    print("Upload Complete. Video ID:", response["id"])
    return response

if _name_ == "_main_":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Video file to upload")
    parser.add_argument("--title", help="Video title", default="Automated Short")
    parser.add_argument("--desc", help="Description", default="Auto uploaded short")
    parser.add_argument("--tags", help="Comma separated tags", default="")
    args = parser.parse_args()

    youtube = get_authenticated_service()
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
    upload_video(youtube, args.file, args.title, args.desc, tags)
