#!/bin/bash
set -e

PROMPT="$1"
if [ -z "$PROMPT" ]; then
  echo "Usage: ./run_pipeline.sh \"Short script or prompt here\""
  exit 1
fi

python3 generate_short.py "$PROMPT"
# find latest output file
FILE=$(ls -t ./output/*.mp4 | head -n1)
echo "Uploading $FILE ..."
python3 youtube_upload.py "$FILE" --title "$PROMPT" --desc "Auto-generated short"
