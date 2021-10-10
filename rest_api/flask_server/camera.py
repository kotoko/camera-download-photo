#!/usr/bin/env python3

import base64
import cv2 as cv
import io
import itertools
import numpy as np
from PIL import Image
import pybullet as pb
import pyrealsense2 as rs
import roslibpy
import rosMsgs
import tempfile
import time


class InternalFrameFormat:
	def __init__(self, width = 0, height = 0, color = [], depth = []):
		self.width = width
		self.height = height
		self.color = color
		self.depth = depth

		resolution = width * height

		if resolution != 0:
			self.color_bpp = len(color) // resolution
			self.depth_bpp = len(depth) // resolution
		else:
			self.color_bpp = 0
			self.depth_bpp = 0

		assert(self.width >= 0)
		assert(self.height >= 0)
		assert(self.color_bpp % 3 == 0)
		if resolution != 0:
			assert(len(color) % resolution == 0)
			assert(len(depth) % resolution == 0)
		else:
			assert(len(color) == 0)
			assert(len(depth) == 0)


# Osobno obrazek RGB i osobno głębokości
def exportToRGB_D(frame: InternalFrameFormat):
	return {
		'width': frame.width,
		'height': frame.height,
		'color': frame.color,
		'color_length': len(frame.color),
		'color_bpp': frame.color_bpp,
		'depth': frame.depth,
		'depth_length': len(frame.depth),
		'depth_bpp': frame.depth_bpp,
	}


# Jedna lista w której są na przemian piksele koloru i głębokości
def exportToRGBD(frame: InternalFrameFormat):
	color_length = len(frame.color)
	depth_length = len(frame.depth)

	rgbd = []
	i = 0
	j = 0
	n = 0
	while i < color_length and j < depth_length:
		for k in range(0, frame.color_bpp):
			rgbd.append(frame.color[i + k])
			n = n + 1
		for k in range(0, frame.depth_bpp):
			rgbd.append(frame.depth[j + k])
			n = n + 1
		i = i + frame.color_bpp
		j = j + frame.depth_bpp

	return {
		'width': frame.width,
		'height': frame.height,
		'rgbd': rgbd,
		'rgbd_length': n,
		'color_bpp': frame.color_bpp,
		'depth_bpp': frame.depth_bpp,
	}


# Obrazek w formacie png
def exportToPNG(frame: InternalFrameFormat):
	png = []
	bytIO = io.BytesIO()

	if frame.color_bpp > 3:
		raise NotImplemented()

	i = 0
	rgbArray = []
	for _ in range(frame.height):
		for _ in range(frame.width):
			pixel = []
			for _ in range(frame.color_bpp):
				pixel.append(frame.color[i])
				i = i + 1
			rgbArray.append(tuple(pixel))

	newimage = Image.new('RGB', (frame.width, frame.height))
	newimage.putdata(rgbArray)
	newimage.save(bytIO, format="png")

	bytIO.seek(0)
	png = [int(x) for x in bytIO.read()]

	#bytIO.seek(0)
	#with tempfile.NamedTemporaryFile(delete=False) as f:
	#	f.write(bytIO.read())
	#	print("PNG file saved at: {}".format(f.name))

	return {
		'width': frame.width,
		'height': frame.height,
		'png': png,
		'png_length': len(png),
	}


# Wyślij obrazek do serwera Rosa
class UploaderRos:
	def __init__(self, host, port):
		self.__ros = roslibpy.Ros(host=host, port=port)
		self.__ros.run()
		self.__talker_color = None
		self.__talker_depth = None

	def __del__(self):
		if self.__ros.is_connected:
			self.__ros.close()  # BUG (see below)

	def exportToRos(self, frame: InternalFrameFormat, topicColor, topicDepth):
		self.__talker_color = roslibpy.Topic(self.__ros, topicColor, rosMsgs.Image.msg_type)
		self.__talker_depth = roslibpy.Topic(self.__ros, topicDepth, rosMsgs.Image.msg_type)
		self.__talker_color.advertise()
		self.__talker_depth.advertise()

		header = roslibpy.Header(1, roslibpy.Time.now(), 'frame???')  # TODO: set frame_id
		bigEndian = 0  # What order of bytes?

		assert(frame.color_bpp == 3)
		assert(frame.depth_bpp == 2)

		color_image = rosMsgs.Image(header, frame.height, frame.width, 'RGB8', bigEndian, frame.color_bpp, frame.color)
		depth_image = rosMsgs.Image(header, frame.height, frame.width, 'Z16', bigEndian, frame.depth_bpp, frame.depth)

		self.__talker_color.publish(color_image)
		self.__talker_depth.publish(depth_image)

		self.__talker_color.unadvertise()
		self.__talker_depth.unadvertise()


# Pobranie przez bilbiotekę realsense w pythonie
class WorkerUSBRealsense:
	def getFrame(self, width, height):
		cfg = rs.config()
		cfg.enable_stream(rs.stream.color, width=width, height=height, format=rs.format.rgb8)
		cfg.enable_stream(rs.stream.depth, width=width, height=height, format=rs.format.z16)

		pipe = rs.pipeline()
		pipe.start(cfg)

		# Ignore frames in the beginning, so autoexposure apply
		for i in range(0, 100):
			frames = pipe.wait_for_frames()
			color = frames.get_color_frame()
			depth = frames.get_depth_frame()

		# Get 1 frame
		frames = pipe.wait_for_frames()
		color = frames.get_color_frame()
		depth = frames.get_depth_frame()

		width = color.get_width()
		height = color.get_height()

		# Convert to list of ints
		colorData = self.__flatten(np.asanyarray(color.get_data(), dtype=np.uint8).tolist(), 2)
		assert(width * height * 3 == len(colorData))

		# Convert to list of ints
		depthData = self.__flatten(np.asanyarray(depth.get_data(), dtype=np.uint16).tolist())
		depthData = self.__flatten([[x % 256, x // 256] for x in depthData])  # What order of bytes?
		assert(width * height * 2 == len(depthData))

		pipe.stop()

		return InternalFrameFormat(width=width, height=height, color=colorData, depth=depthData)

	def __flatten(self, data, n=1):
		if n <= 0:
			return data
		return self.__flatten(list(itertools.chain.from_iterable(data)), n-1)


# Pobierz z serwera ros-owego
class WorkerRos:
	def __init__(self, host, port):
		self.__ros = roslibpy.Ros(host=host, port=port)
		self.__ros.run()
		self.__colorMsg = None
		self.__depthMsg = None
		self.__listenerColor = None
		self.__listenerDepth = None

	def __del__(self):
		if self.__ros.is_connected:
			# BUG
			# For some reason calling close()
			# causes error "server did not drop TCP connection in time"
			# in websocket library. This error causes situation that
			# you can not reconnect again until you restart program.

			self.__ros.close()

	def getFrame(self, topicColor, topicDepth):
		((cw, ch, cd), (dw, dh, dd)) = self.__getOneFrame(topicColor, topicDepth)

		assert(cw == dw)
		assert(ch == dh)

		return InternalFrameFormat(width=cw, height=ch, color=cd, depth=dd)

	def __callbackColor(self, msg):
		if self.__colorMsg is None:
			self.__colorMsg = msg

		self.__listenerColor.unsubscribe()

	def __callbackDepth(self, msg):
		if self.__depthMsg is None:
			self.__depthMsg = msg

		self.__listenerDepth.unsubscribe()

	def __getOneFrame(self, topicColor, topicDepth):
		self.__colorMsg = None
		self.__depthMsg = None

		self.__listenerColor = roslibpy.Topic(self.__ros, topicColor, 'sensor_msgs/Image')
		self.__listenerDepth = roslibpy.Topic(self.__ros, topicDepth, 'sensor_msgs/Image')

		self.__listenerColor.subscribe((lambda s: s.__callbackColor)(self))
		self.__listenerDepth.subscribe((lambda s: s.__callbackDepth)(self))

		while self.__listenerColor.is_subscribed or self.__listenerDepth.is_subscribed:
			time.sleep(0.2)

		c = self.__colorMsg
		d = self.__depthMsg
		self.__colorMsg = None
		self.__depthMsg = None

		colorWidth = c["width"]
		colorHeight = c["height"]
		colorData = [int(b) for b in base64.b64decode(c["data"])]

		depthWidth = d["width"]
		depthHeight = d["height"]
		depthData = [int(b) for b in base64.b64decode(d["data"])]

		# TODO
		# Potentially change orders of depth bytes.
		# Look at:
		#   d["encoding"], d["is_bigendian"]

		return ((colorWidth, colorHeight, colorData), (depthWidth, depthHeight, depthData))


# Pobierz ze zwykłej kamerki korzystając z opencv
class WorkerOpencv:
	def __init__(self, device):
		self.__videoCapture = cv.VideoCapture(device)
		if not self.__videoCapture.isOpened():
			raise Exception("Could not open video device")

	def __del__(self):
		self.__videoCapture.release()

	def getFrame(self, width, height):
		self.__videoCapture.set(cv.CAP_PROP_FRAME_WIDTH, width)
		self.__videoCapture.set(cv.CAP_PROP_FRAME_HEIGHT, height)

		(rc, frame) = self.__videoCapture.read()
		if not rc:
			raise Exception("Could not get frame from video device")

		frameRGB = frame[:,:,::-1]  # BGR => RGB
		color = self.__flatten(np.asanyarray(frameRGB, dtype=np.uint8).tolist(), 2)

		width = len(frameRGB[0])
		height = len(frameRGB)
		depth = [0] * (width * height * 2)

		return InternalFrameFormat(width=width, height=height, color=color, depth=depth)

	def __flatten(self, data, n=1):
		if n <= 0:
			return data
		return self.__flatten(list(itertools.chain.from_iterable(data)), n-1)


# Pobierz z symulatora pybullet
class WorkerPybullet:
	def __init__(self, mode, host, port):
		if mode == "udp":
			self.__physicsClientID = pb.connect(pb.UDP, host, port)
		elif mode == "tcp":
			self.__physicsClientID = pb.connect(pb.TCP, host, port)
		else:
			raise NotImplementedError

	def __del__(self):
		pb.disconnect(self.__physicsClientID)

	def getFrame(self, width, height, eyePosition, eyeUpVector, targetPosition, fov, aspect, nearDistance, farDistance):
		viewMatrix = pb.computeViewMatrix(
			cameraEyePosition=eyePosition,
			cameraTargetPosition=targetPosition,
			cameraUpVector=eyeUpVector)

		projectionMatrix = pb.computeProjectionMatrixFOV(
			fov=fov,
			aspect=aspect,
			nearVal=nearDistance,
			farVal=farDistance)

		width2, height2, rgbaImg, depthImg, _segImg = pb.getCameraImage(
			width=width,
			height=height,
			viewMatrix=viewMatrix,
			projectionMatrix=projectionMatrix,
			physicsClientId=self.__physicsClientID)

		colorData = [x for i, x in enumerate(self.__flatten(rgbaImg.tolist(), 2)) if i % 4 != 3]  # RGBA => RGB

		# pybullet returns depth as float in range [0.0 ; 1.0]
		# Convert it here to uint16 in range [0 ; 65535]
		depthData = np.array(self.__flatten(depthImg))

		depthData = (depthData * 65535)  # [0.0 ; 1.0]  => [0 ; 65535]
		depthData = depthData.astype(int)  # Take integer part

		# Make sure that range is correct
		depthData[depthData > 65535] = 65535
		depthData[depthData < 0] = 0

		# Cast numpy.int64 to simple python int
		depthData = [int(x) for x in depthData]

		# Change representation to bytes
		depthData = self.__flatten([[x % 256, x // 256] for x in depthData])  # What order of bytes?
		assert(width2 * height2 * 2 == len(depthData))

		return InternalFrameFormat(width=width2, height=height2, color=colorData, depth=depthData)

	def __flatten(self, data, n=1):
		if n <= 0:
			return data
		return self.__flatten(list(itertools.chain.from_iterable(data)), n-1)


# Główna funkcja, która zwraca dane
def getFrame(input, output, width, height, workerRosCfg=None, workerPybulletCfg=None, workerOpencvCfg=None, uploadRosCfg=None):
	frame = InternalFrameFormat()

	if input == "usb_realsense":
		w = WorkerUSBRealsense()
		frame = w.getFrame(width, height)
	elif input == "ros":
		w = WorkerRos(workerRosCfg["host"], workerRosCfg["port"])
		frame = w.getFrame(workerRosCfg["topic_color"], workerRosCfg["topic_depth"])
	elif input == "opencv":
		w = WorkerOpencv(workerOpencvCfg["device"])
		frame = w.getFrame(width, height)
	elif input == "pybullet":
		w = WorkerPybullet(mode=workerPybulletCfg['mode'], host=workerPybulletCfg['host'], port=workerPybulletCfg['port'])
		frame = w.getFrame(width, height, eyePosition=workerPybulletCfg['eye_position'], eyeUpVector=workerPybulletCfg['eye_up_vector'],
			targetPosition=workerPybulletCfg['target_position'], fov=workerPybulletCfg['fov'], aspect=workerPybulletCfg['aspect'],
			nearDistance=workerPybulletCfg['near_distance'], farDistance=workerPybulletCfg['far_distance'])
	else:
		raise NotImplementedError("Not recognised input method: {}".format(input))

	if output == "rgb+d":
		return exportToRGB_D(frame)
	elif output == "rgbd":
		return exportToRGBD(frame)
	elif output == "png":
		return exportToPNG(frame)
	elif output == "ros":
		u = UploaderRos(uploadRosCfg["host"], uploadRosCfg["port"])
		u.exportToRos(frame, uploadRosCfg["topic_color"], uploadRosCfg["topic_depth"])
		return {}
	else:
		raise NotImplementedError("Not recognised output format: {}".format(output))
