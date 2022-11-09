#!/bin/bash

ffmpeg -i clip.mp4 -vf crop=300:300 clip_cropped.mp4

