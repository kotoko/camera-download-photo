# rest_api

REST service is written in python using [flask](https://flask.palletsprojects.com/en/2.0.x/index.html). It can download photo + depth from 4 sources.

1. *Simple camera* (no depth data). Almost all laptops have integrated webcams. If your operating system (V4L2) can detect camera then REST service can download photo from that camera.

2. *Intel RealSense camera through USB cable*. Lets say that you have Intel RealSense camera. Install [official driver](https://github.com/IntelRealSense/librealsense/). Connect camera to computer. If you did it correctly REST service will be able to download photo from RealSense camera.

3. *Intel RealSense camera through ROS server*. Lets say that you have Intel RealSense camera. If you have already running ROS server then connect camera to that computer, install driver and *rosbridge_server*. REST service should be able to download photo from ROS server. \
If you don't have already running ROS server you can use docker container from directory `worker_docker_ros_usb_realsense/ros_usb_realsense/`. It automatically installs driver and *rosbridge_server* inside container on your local computer. REST service should be able to download photo from ROS server installed inside docker.

4. *Virtual camera inside pybullet simulation*. If you want download photo from pybullet simulation you need to run network bridge first. It is developed by authors of pybullet. Network bridge uses shared memory to communicate with pybullet server so make sure to configure parameters correctly. Example is in directory `example_pybullet_server/`. 1. Run pybullet server. 2. Run network bridge. 3. REST service should be able to download photo from virtual camera. \
Please note that virtual camera is not an object in pybullet but only viewport transformations. If you want to change camera parameters see `/camera/request_config`.

## Install dependencies

This service was created (therefore tested) with *linux* and *python* ≥3.7 in mind.

Install python dependencies (in virtual environment):

```
cd flask_server/
make prepare
```

## Run REST service

```
cd flask_server/
make run
```

## Endpoints

REST service provides following endpoints:

1. `/camera/<inputMethod>/<outputFormat>` : GET
1. `/camera/request_config` : GET, POST

`<inputMethod>` is one of: `usb_realsense`, `ros`, `pybullet`, `opencv`.

`<outputFormat>` is one of: `rgb+d`, `rgbd`, `png`, `ros`.

### Sample responses

#### `/camera/<inputMethod>/rgb+d`

```
{
	height       : 1,
	width        : 2,
	color        : [1, 1, 1, 2, 2, 2],
	color_bpp    : 3,
	color_length : 6,
	depth        : [101, 101, 102, 102],
	depth_bpp    : 2,
	depth_length : 4,
}
```

`depth` (Z16) and `color` (RGB8) contain numbers from range [0-255] (bytes).

#### `/camera/<inputMethod>/rgbd`

```
{
	height      : 1,
	width       : 2,
	color_bpp   : 3,
	depth_bpp   : 2,
	rgbd        : [1, 1, 1, 101, 101, 2, 2, 2, 102, 102],
	rgbd_length : 10,
}
```

`rgbd` contains numbers from range [0-255] (bytes). Three bytes of color (RGB8) interwined with two bytes of depth (Z16).

#### `/camera/<inputMethod>/png`

```
{
	height     : 1,
	width      : 2,
	png        : [1, 2, 3, 4, 5, ...],
	png_length : 123,
}
```

`png` contains numbers from range [0-255] (bytes - file on disk).

#### `/camera/request_config`

```
{
	camera_height                   : 720,
	camera_width                    : 1280,
	upload_ros_host                 : "127.0.0.1",
	upload_ros_port                 : 9090,
	upload_ros_topic_color          : "/fake_camera/color",
	upload_ros_topic_depth          : "/fake_camera/depth",
	worker_opencv_device            : 0,
	worker_ros_host                 : "127.0.0.1",
	worker_ros_port                 : 9090,
	worker_ros_topic_color          : "/camera/color/image_raw",
	worker_ros_topic_depth          : "/camera/depth/image_rect_raw",
	worker_pybullet_host            : "127.0.0.1",
	worker_pybullet_mode            : "tcp",
	worker_pybullet_port            : 6667,
	worker_pybullet_eye_position    : [0, 0, 3],
	worker_pybullet_eye_up_vector   : [0, 1, 0],
	worker_pybullet_target_position : [0, 0, 0],
	worker_pybullet_aspect          : 1.0,
	worker_pybullet_fov             : 45.0,
	worker_pybullet_far_distance    : 3.1,
	worker_pybullet_near_distance   : 0.1,
}
```

REST service configuration is written in file `flask_server/config.toml`. File is generated on first use.

## Run ROS server in docker container

It is possible that you have already running ROS server with connected RealSense camera to it. In this scenario you just need to make sure that *rosbridge_server* is also running. REST service will be able to connect to ROS server with no extra work.

However it is also possible that you have RealSense camera and would want to run ROS server locally. For this scenario i created small docker container with ROS server inside.

Connect RealSense camera to computer. Then build and start container:

```
cd worker_docker_ros_usb_realsense/
bash build.sh
bash run_rosnode.sh
```

Wait about 10-20 seconds. ROS server is running and RealSense camera should be visible as topic.

When container is running you can see logs:

```
docker logs -f CONTAINER_ID
```

When finished stop container:

```
docker stop CONTAINER_ID
```

## Compile pybullet network bridge

If you want to connect to pybullet server you need network bridge. Short instruction of compilation:

```
git clone --depth 1 -b master --single-branch \
    ’https://github.com/bulletphysics/bullet3.git’
cd bullet3/
cd build3/
./premake4_linux --double gmake    # <- only 32-bit linux
./premake4_linux64 --double gmake  # <- only 64-bit linux
cd gmake/
make -j8 App_PhysicsServerSharedMemoryBridgeUDP \
    App_PhysicsServerUDP \
    App_PhysicsServerSharedMemoryBridgeTCP \
    App_PhysicsServerTCP
cd ../../../
```

In directory `bullet3/bin/` should be binary files.

`App_PhysicsServerSharedMemoryBridgeUDP` and `App_PhysicsServerSharedMemoryBridgeTCP` connect to already running pybullet server using shared memory.

`App_PhysicsServerUDP` and `App_PhysicsServerTCP` start new pybullet server internally.

You can change listening port with parameter `--port:=1234` .

## Bugs and other stuff

* This REST service was only tested with camera Intel RealSense D415 (color: `RGB8`, depth: `Z16`, resolution: `1280x720`). Other RealSense models may work out of the box or require changes to codebase.

* Author of this project was running Gentoo Linux and developed program on that distribution.

* Current implementation on every HTTP request: 1. initiates connection to camera; 2. downloads photo; 3 closes connection. In practice it means that only one user can simultaneously do HTTP requests because only one program can have exclusive access to video stream.

* Downloading from ROS server is bugged. For unknown reason to me when REST service disconnects from ROS server, client library (in REST service) goes into bugged state and can not connect to the ROS server anymore. In practice it means after downloading first photo each following download request fails. As a workaround you can restart both ROS server and REST service and download one photo again.
