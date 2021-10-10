#  camera-download-photo

This is simple REST service that can download photo from:

* simple camera (V4l2, through opencv library, no depth data),
* Intel® RealSense™ camera connected using USB cable (using official driver),
* Intel® RealSense™ camera connected to ROS server (using *rosbridge_server*),
* virtual camera inside pybullet simulation

and share data (photo + depth) in unified format (integer arrays in JSON).

## Content of repository

In directory `rest_api/` is REST service.

In directory `example_of_using_rest_api/` is simple python script that downloads photo using REST service and exemplary process the data.

## Project status

This project is published "as is" in the spirit of "proof of concept". No support or updates are provided. If you found this program usefull I encourage you to fork it and/or download offline copy.

## License

See file `License`.
