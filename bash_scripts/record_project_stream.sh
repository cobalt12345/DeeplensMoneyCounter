#!/bin/bash

#mplayer -demuxer lavf /opt/awscam/out/ch1_out.h264 -dumpstream -dumpfile clip.mp4
ffmpeg -framerate 24 -i /opt/awscam/out/ch1_out.h264 -c copy clip.mp4
