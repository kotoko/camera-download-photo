#!/usr/bin/env python3

import argparse
import cv2 as cv
import io
import numpy as np
import math
import pathlib
import tempfile
import time
import requests


def detectCircles(image, param2=40):
	maxRadius = min(len(image), len(image[0])) // 3
	minRadius = min(len(image), len(image[0])) // 16

	# Detect circles
	circles = cv.HoughCircles(image, cv.HOUGH_GRADIENT, 1, param1=200, param2=param2, minDist=minRadius*2+5, minRadius=minRadius, maxRadius=maxRadius)

	if circles is None:
		return []

	# [(X, Y, r)]
	circles = [(int(c[0]), int(c[1]), round(c[2], 1)) for c in circles[0]]

	return circles


def onlyBigCircles(circles):
	assert(len(circles) >= 2)

	# Find maximum size
	bigDiameter = max([c[2] for c in circles])

	# Remember circle only if it"s >=85% of bigDiameter (>=70% of area)
	circles2 = [c for c in circles if c[2] >= bigDiameter * 0.85]

	# Edge case. Add second biggest circle to the result
	if len(circles2) == 1:
		circles3 = sorted(circles, key=lambda c: c[2], reverse=True)
		circles2.append(circles3[1])

	return circles2


def findLeftAndRightCircles(circles):
	assert(len(circles) >= 2)

	circles2 = sorted(circles, key=lambda c: c[0])

	left = circles2[0]
	right = circles2[-1]

	return (left,right)


def drawStuff(image, circles):
	assert(len(circles) >= 2)

	# Draw detected circles
	for pt in circles:
		x, y, r = pt[0], pt[1], int(pt[2])

		# Draw the circumference of the circle
		cv.circle(image, (x, y), r, (0, 0, 255), 2)

		# Draw a small circle (of radius 1) to show the center
		cv.circle(image, (x, y), 1, (0, 0, 255), 3)

	left = circles[0]
	right = circles[1]

	# Draw line between circles
	cv.line(image, (left[0], left[1]), (right[0],right[1]), (0, 0, 255), thickness=2)

	# Print text with distance value
	dist = math.sqrt((left[0] - right[0])**2 + (left[1] - right[1])**2)
	text = "distance: " + str(round(dist, 1))
	cv.putText(image, text, (8,24), cv.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(0, 0, 255), thickness=2)

	# Show picture
	cv.imshow("Calculate distance between balls", image)

	print("Press Ctrl+C in shell or any key on keyboard in window to close program")
	try:
		cv.waitKey(200)  # Somehow this function call forces image to show
		while True:
			time.sleep(0.2)
			if cv.pollKey() != -1:
				break
	finally:
		cv.destroyAllWindows()


def readFromFile(imgPath):
	# Read image
	return cv.imread(imgPath, cv.IMREAD_COLOR)


def readFromAPI(host, port, inputMethod):
	if ":" in host:
		raise NotImplementedError("IPv6 support is not implemented")

	# Download png image
	r = requests.get("http://{}:{}/camera/{}/png".format(host, port, inputMethod))

	if r.status_code != 200:
		print("REST API returned response code different than 200: {}. Aborting...".format(r.status_code))
		raise ConnectionError

	# Create file-like object
	imgIO = io.BytesIO()
	for x in r.json()["png"]:
		imgIO.write(x.to_bytes(1, "big"))

	# DEBUG
	#imgIO.seek(0)
	#with tempfile.NamedTemporaryFile(delete=False) as f:
	#	f.write(imgIO.read())
	#	print("PNG saved at: {}".format(f.name))

	# Read image
	imgIO.seek(0)
	return cv.imdecode(np.frombuffer(imgIO.read(), dtype=np.uint8), cv.IMREAD_COLOR)


def parseArgs():
	parser = argparse.ArgumentParser()

	mode = parser.add_mutually_exclusive_group(required=True)
	mode.add_argument(
		"--api",
		help="read image from REST API",
		action="store_true")
	mode.add_argument(
		"--file",
		metavar="PATH",
		help="read image from file",
		type=str)

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
	parser.add_argument(
		"--inputMethod",
		help="input method for REST API (default: usb_realsense)",
		type=str,
		default="usb_realsense",
		choices=["opencv", "pybullet", "ros", "usb_realsense"])

	return parser.parse_args()


if __name__ == "__main__":
	# Parse arguments passed to program
	args = parseArgs()

	# Picture on disk
	if args.file:
		imageOrig = readFromFile(args.file)

	# Picture from REST API
	if args.api:
		imageOrig = readFromAPI(args.host, args.port, args.inputMethod)

	if imageOrig is None:
		raise FileNotFoundError(imgPath)

	# DEBUG
	#cv.imshow("DEBUG_PREVIEW", imageOrig)
	#cv.waitKey(1000*8)
	#cv.destroyAllWindows()

	# Transform image for shape detection
	image = cv.cvtColor(imageOrig, cv.COLOR_BGR2GRAY)
	image = cv.blur(image, (3, 3))

	# DEBUG
	#cv.imshow("DEBUG_PREVIEW_2", image)
	#cv.waitKey(1000*8)
	#cv.destroyAllWindows()

	# Detect circles
	for param2 in [200, 150, 100, 80, 60, 50, 45, 40, 35, 30, 25, 20, 15, 10]:
		circles = detectCircles(image, param2=param2)

		if len(circles) >= 2:
			break

	if len(circles) < 2:
		print("Found less than 2 circle shapes in image! (Found: {}) Aborting...".format(len(circles)))
		raise SystemExit

	# Get rid of small circles that are probably just noise
	circles = onlyBigCircles(circles)

	# Find circle most on left side and most on right side
	left,right = findLeftAndRightCircles(circles)

	# Draw result
	drawStuff(imageOrig, [left, right])
