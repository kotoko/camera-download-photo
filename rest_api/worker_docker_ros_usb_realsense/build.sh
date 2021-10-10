#!/bin/bash

MY_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

docker build -t ros_usb_realsense "$MY_DIR/ros_usb_realsense"
