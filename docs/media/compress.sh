#!/bin/bash
# cSpell:ignore vcodec,acodec
for FILE in *.mov; do
    ffmpeg -i "${FILE}" -vcodec h264 -acodec mp2  "${FILE%.*}.mp4"
done
