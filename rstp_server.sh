#!/bin/bash
mediamtx_id=$(sudo docker run --rm -d --network=host bluenviron/mediamtx:latest)
echo "Waiting for the server to start..."
sleep 3
ffmpeg \
    -re \
    -stream_loop -1 \
    -i input.mp4 \
    -an \
    -c:v copy \
    -f rtsp rtsp://localhost:8554/example
sudo docker stop $mediamtx_id
