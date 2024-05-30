# video_tracker

Simple video tracker in Python. Depends only on OpenCV.

## Features:
* Attempt to recover last target
* Detect degenerated bounding box when target is close to edge
* Allow target correction

## How to use:

1. Choose RTSP stream. Example rtsp server, run by ```./rstp_server.sh``` can be used. (It requires addictional dependencies: ffmpeg, docker, mediamtx etc.)

2. Run ```main.py``` - example usage of VideoTracker class.