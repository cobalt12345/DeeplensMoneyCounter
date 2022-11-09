#!/bin/bash

#mplayer -demuxer lavf /opt/awscam/out/ch1_out.h264
mplayer -demuxer lavf -lavfdopts format=mjpeg:probesize=32 /tmp/results.mjpeg

