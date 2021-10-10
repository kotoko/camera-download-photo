#!/bin/bash

docker image rm -f ros_usb_realsense
docker image rm -f ros:noetic-robot
docker image prune
