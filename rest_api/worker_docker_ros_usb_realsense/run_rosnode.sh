#!/bin/bash

MY_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
VOLUMES="-v $MY_DIR:/root/src"

xhost +local:root; docker run -d --network host --env DISPLAY=$DISPLAY $VOLUMES -v /tmp/.X11-unix:/tmp/.X11-unix --privileged ros_usb_realsense

#xhost +local:root; docker run -d --network host --env DISPLAY=$DISPLAY $VOLUMES -v $XAUTH:/root/.Xauthority -v /tmp/.X11-unix:/tmp/.X11-unix --privileged ros_usb_realsense
