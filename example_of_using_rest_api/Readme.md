# example_of_using_rest_api

This is simple python script that downloads photo from REST service. Then tries to detect two shapes in the photo - two circles and calculates distance between centers (in pixels).

## Install dependencies

Download and install dependencies:

```
make prepare
```

Before running python script you need to activate environment:

```
source venv/bin/activate
```

You need to activate environment everytime you open new bash session.

## Run script

Make sure that everything is OK by calling script with `--help` flag:

```
./recognize.py --help
```

You should see something like this:

```
usage: recognize.py [-h] (--api | --file PATH)
	[--host IPv4]
	[--port PORT]
	[--inputMethod {opencv,pybullet,ros,usb_realsense}]

optional arguments:
-h, --help            show this help message and exit
--api                 read image from REST API
--file PATH           read image from file
--host IPv4           IP address of REST API server (default: 127.0.0.1)
--port PORT           port number of REST API server (default: 5000)
--inputMethod {opencv,pybullet,ros,usb_realsense}
                      input method for REST API (default: usb_realsense)
```

### Process photo from file

You can process photo from file passing filepath:

```
./recognize.py --file "./photo.jpg"
```

In repository there is sample `photo.jpg` file.

Done!

### Process photo from RealSense camera (official driver)

Make sure REST service is running and make sure that RealSense camera is connected through USB cable to the computer.

Send configuration (mostly preffered photo resolution):

```
./send-config.py --host 127.0.0.1 --port 5000 --usb_realsense
```

Download and process photo:

```
./recognize.py --api --host 127.0.0.1 --port 5000 --inputMethod usb_realsense
```

Done!

### Process photo from RealSense camera (ROS server)

Make sure ROS server is running and make sure that RealSense camera is connected through USB cable to the computer. Make sure REST service is running.

Send configuration (mostly ROS server IP address & port number):

```
./send-config.py --host 127.0.0.1 --port 5000 --ros
```

Download and process photo:

```
./recognize.py --api --host 127.0.0.1 --port 5000 --inputMethod ros
```

Done!

### Process photo from virtual camera (pybullet)

Run pybullet simulation (with shared memory access):

```
make runPybulletServer
```

Run pybullet network bridge:

```
bullet3/bin/App_PhysicsServerSharedMemoryBridgeTCP_gmake_x64_release --port:=6667
```

Make sure REST service is running. Send configuration (mostly pybullet bridge IP address & port number):

```
./send-config.py --host 127.0.0.1 --port 5000 --pybullet
```

Download and process photo:

```
./recognize.py --api --host 127.0.0.1 --port 5000 --inputMethod pybullet
```

Done!

### Process photo from simple camera (V4L2)

Make sure REST service is running and make sure that camera is detected by operating system.

Send configuration (mostly preffered photo resolution):

```
./send-config.py --host 127.0.0.1 --port 5000 --opencv
```

Download and process photo:

```
./recognize.py --api --host 127.0.0.1 --port 5000 --inputMethod opencv
```

Done!

## Compile pybullet network bridge

Short instruction:

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
