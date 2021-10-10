#!/usr/bin/env python3

from flask import Flask
from flask import jsonify
from flask import request
import camera
import config

app = Flask(__name__)


def getFrame(input, output):
	cfg = config.getConfig()
	width = cfg['camera']['width']
	height = cfg['camera']['height']
	ros = cfg['worker_ros']
	ros2 = cfg['upload_ros']
	opencv = cfg['worker_opencv']
	pybullet = cfg['worker_pybullet']

	return camera.getFrame(input=input, output=output, width=width, height=height, workerRosCfg=ros, workerOpencvCfg=opencv, workerPybulletCfg=pybullet, uploadRosCfg=ros2)


@app.route("/")
def homepage():
	return """
		<p>/camera/usb_realsense</p>
		<p>/camera/ros</p>
		<p>/camera/opencv</p>
		<p>/camera/pybullet</p>
		<br/>
		<p>/camera/request_config (parametry wysyłane do kamery do zrobienia zdjęcia)</p>
	"""


def supportedFormats():
	return "<p>Supported formats: rgb+d rgbd png ros</p>"


@app.route("/camera/usb_realsense")
def workerUSBRealsenseHelp():
	return supportedFormats()


@app.route("/camera/usb_realsense/<string:dataFormat>")
def workerUSBRealsense(dataFormat):
	return jsonify(getFrame(input="usb_realsense", output=dataFormat))


@app.route("/camera/opencv/<string:dataFormat>")
def workerOpencv(dataFormat):
	return jsonify(getFrame(input="opencv", output=dataFormat))


@app.route("/camera/opencv")
def workerOpencvHelp():
	return supportedFormats()


@app.route("/camera/ros")
def workerROSHelp():
	return supportedFormats()


@app.route("/camera/ros/<string:dataFormat>")
def workerROS(dataFormat):
	return jsonify(getFrame(input="ros", output=dataFormat))


@app.route("/camera/pybullet")
def workerPybulletHelp():
	return supportedFormats()


@app.route("/camera/pybullet/<string:dataFormat>")
def workerPybullet(dataFormat):
	return jsonify(getFrame(input="pybullet", output=dataFormat))


@app.route("/camera/request_config", methods=["GET", "POST"])
def requestConfig():
	cfg = config.getConfig()

	if request.method == 'POST':
		# [camera]
		if 'camera_width' in request.form:
			cfg['camera']['width'] = int(request.form['camera_width'])

		if 'camera_height' in request.form:
			cfg['camera']['height'] = int(request.form['camera_height'])

		# [worker_ros]
		if 'worker_ros_topic_color' in request.form:
			cfg['worker_ros']['topic_color'] = request.form['worker_ros_topic_color']

		if 'worker_ros_topic_depth' in request.form:
			cfg['worker_ros']['topic_depth'] = request.form['worker_ros_topic_depth']

		if 'worker_ros_host' in request.form:
			cfg['worker_ros']['host'] = request.form['worker_ros_host']

		if 'worker_ros_port' in request.form:
			cfg['worker_ros']['port'] = int(request.form['worker_ros_port'])

		# [upload_ros]
		if 'upload_ros_topic_color' in request.form:
			cfg['upload_ros']['topic_color'] = request.form['upload_ros_topic_color']

		if 'upload_ros_topic_depth' in request.form:
			cfg['upload_ros']['topic_depth'] = request.form['upload_ros_topic_depth']

		if 'upload_ros_host' in request.form:
			cfg['upload_ros']['host'] = request.form['upload_ros_host']

		if 'upload_ros_port' in request.form:
			cfg['upload_ros']['port'] = int(request.form['upload_ros_port'])

		# [worker_opencv]
		if 'worker_opencv_device' in request.form:
			try:
				dev = int(request.form['worker_opencv_device'])
			except ValueError:
				dev = request.form['worker_opencv_device']
			cfg['worker_opencv']['device'] = dev

		# [worker_pybullet]
		if 'worker_pybullet_mode' in request.form:
			cfg['worker_pybullet']['mode'] = request.form['worker_pybullet_mode']

		if 'worker_pybullet_host' in request.form:
			cfg['worker_pybullet']['host'] = request.form['worker_pybullet_host']

		if 'worker_pybullet_port' in request.form:
			cfg['worker_pybullet']['port'] = int(request.form['worker_pybullet_port'])

		if 'worker_pybullet_eye_position' in request.form:
			cfg['worker_pybullet']['eye_position'] = map(int, request.form.getlist('worker_pybullet_eye_position'))

		if 'worker_pybullet_eye_up_vector' in request.form:
			cfg['worker_pybullet']['eye_up_vector'] = map(int, request.form.getlist('worker_pybullet_eye_up_vector'))

		if 'worker_pybullet_target_position' in request.form:
			cfg['worker_pybullet']['target_position'] = map(int, request.form.getlist('worker_pybullet_target_position'))

		if 'worker_pybullet_fov' in request.form:
			cfg['worker_pybullet']['fov'] = float(request.form['worker_pybullet_fov'])

		if 'worker_pybullet_aspect' in request.form:
			cfg['worker_pybullet']['aspect'] = float(request.form['worker_pybullet_aspect'])

		if 'worker_pybullet_near_distance' in request.form:
			cfg['worker_pybullet']['near_distance'] = float(request.form['worker_pybullet_near_distance'])

		if 'worker_pybullet_far_distance' in request.form:
			cfg['worker_pybullet']['far_distance'] = float(request.form['worker_pybullet_far_distance'])

		config.saveConfig(cfg)
		return jsonify({})
	elif request.method == 'GET':
		return jsonify({
			'camera_width': cfg['camera']['width'],
			'camera_height': cfg['camera']['height'],
			'worker_ros_topic_color': cfg['worker_ros']['topic_color'],
			'worker_ros_topic_depth': cfg['worker_ros']['topic_depth'],
			'worker_ros_host': cfg['worker_ros']['host'],
			'worker_ros_port': cfg['worker_ros']['port'],
			'upload_ros_topic_color': cfg['upload_ros']['topic_color'],
			'upload_ros_topic_depth': cfg['upload_ros']['topic_depth'],
			'upload_ros_host': cfg['upload_ros']['host'],
			'upload_ros_port': cfg['upload_ros']['port'],
			'worker_opencv_device': cfg['worker_opencv']['device'],
			'worker_pybullet_mode': cfg['worker_pybullet']['mode'],
			'worker_pybullet_host': cfg['worker_pybullet']['host'],
			'worker_pybullet_port': cfg['worker_pybullet']['port'],
			'worker_pybullet_eye_position': cfg['worker_pybullet']['eye_position'],
			'worker_pybullet_eye_up_vector': cfg['worker_pybullet']['eye_up_vector'],
			'worker_pybullet_target_position': cfg['worker_pybullet']['target_position'],
			'worker_pybullet_fov': cfg['worker_pybullet']['fov'],
			'worker_pybullet_aspect': cfg['worker_pybullet']['aspect'],
			'worker_pybullet_near_distance': cfg['worker_pybullet']['near_distance'],
			'worker_pybullet_far_distance': cfg['worker_pybullet']['far_distance'],
		})
