#!/bin/bash
# Usage:
# 	define file name using 'export file_name=frame' and file starting index
#	'export file_index=0'
#
# To support a state (file index) between script executions - source this script starting it by '. # capture_single_frame.sh' or 'source capture_single_frame.sh'

if [ -z ${file_name+z} ]
    then
        echo 'Set file_name env variable'
	exit 1   
fi

if [ -z ${file_index+z} ]
    then
	echo 'Set file_index env variable'
	exit 2
fi

file_name_to_save=${file_name}_${file_index}.jpeg
#sudo ffmpeg -f-i /tmp/results.mjpeg -vframes 1 ${file_name_to_save}
sudo ffmpeg -i /tmp/results.mjpeg -vframes 1 ${file_name_to_save}
echo ${file_name_to_save}' saved!'

export file_index=$((file_index+=1))
