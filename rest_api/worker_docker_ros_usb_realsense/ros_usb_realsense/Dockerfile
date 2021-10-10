# Inspired by https://github.com/iory/docker-ros-realsense

FROM ros:noetic-robot
SHELL ["/bin/bash", "-c"]

ENV ROS_DISTRO noetic

RUN apt-get update -qq
RUN apt-get install -y software-properties-common
RUN apt-get install -y ros-noetic-realsense2-camera
RUN apt-get install -y ros-noetic-rosbridge-suite

CMD ["/bin/bash", "-c", " \
      source /opt/ros/noetic/setup.bash ; \
      roslaunch realsense2_camera rs_camera.launch \
        filters:=pointcloud align_depth:=true \
        color_width:=1280 color_height:=720 color_fps:=30 \
        depth_width:=1280 depth_height:=720 depth_fps:=30 \
        & \
      sleep 10 ; \
      roslaunch rosbridge_server rosbridge_websocket.launch \
        port:=9090 \
        address:=0.0.0.0 \
    "]
