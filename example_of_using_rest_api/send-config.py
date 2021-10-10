#!/usr/bin/env python

import argparse
import requests


def worker_opencv():
	return {
		"camera_width": "640",
		"camera_height": "480",
		"worker_opencv_device": 0,
	}


def worker_usb_realsense():
	return {
		"camera_width": "640",
		"camera_height": "480",
	}


def worker_pybullet():
	return {
		"camera_width": "640",
		"camera_height": "480",
		"worker_pybullet_aspect": 1.33,
		"worker_pybullet_eye_position": [0,0,4],
		"worker_pybullet_eye_up_vector": [0,1,0],
		"worker_pybullet_far_distance": 10,
		"worker_pybullet_fov": 45,
		"worker_pybullet_host": "127.0.0.1",
		"worker_pybullet_mode": "tcp",
		"worker_pybullet_near_distance": 0.1,
		"worker_pybullet_port": 6667,
		"worker_pybullet_target_position": [0,0,0],
	}


def worker_ros():
	return {
		"worker_ros_host": "127.0.0.1",
		"worker_ros_port": 9090,
		"worker_ros_topic_color": "/camera/color/image_raw",
		"worker_ros_topic_depth": "/camera/depth/image_rect_raw"
	}


def parseArgs():
	parser = argparse.ArgumentParser()

	mode = parser.add_mutually_exclusive_group(required=True)
	mode.add_argument(
		"--opencv",
		help="send config for opencv method",
		action="store_true")
	mode.add_argument(
		"--pybullet",
		help="send config for pybullet method",
		action="store_true")
	mode.add_argument(
		"--ros",
		help="send config for ros method",
		action="store_true")
	mode.add_argument(
		"--usb_realsense",
		help="send config for usb_realsense method",
		action="store_true")

	parser.add_argument(
		"--host",
		metavar="IPv4",
		help="IP address of REST API server (default: 127.0.0.1)",
		type=str,
		default="127.0.0.1")
	parser.add_argument(
		"--port",
		help="port number of REST API server (default: 5000)",
		type=int,
		default=5000)

	return parser.parse_args()


if __name__ == "__main__":
	# Parse arguments passed to program
	args = parseArgs()

	if args.opencv:
		payload = worker_opencv()

	if args.pybullet:
		payload = worker_pybullet()

	if args.ros:
		payload = worker_ros()

	if args.usb_realsense:
		payload = worker_usb_realsense()

	r = requests.post("http://{}:{}/camera/request_config".format(args.host, args.port), data=payload)
	r.raise_for_status()

	print("DONE!")
