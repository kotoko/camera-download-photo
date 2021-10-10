#!/usr/bin/env python3

import pybullet as p
import pybullet_data
import time

fps = 240


if __name__ == "__main__":
	physicsClientID = p.connect(p.GUI_SERVER)  # GUI_SERVER or SHARED_MEMORY_SERVER

	try:
		p.setGravity(0, 0, -10)

		p.setAdditionalSearchPath(pybullet_data.getDataPath())
		p.loadURDF("plane.urdf", [0, 0, -0.3])

		cubeStartPos1 = [-1,0,0.2]
		cubeStartPos2 = [1,0,0.2]

		cube1 = p.loadURDF("sphere2red.urdf",cubeStartPos1)
		cube2 = p.loadURDF("sphere2red.urdf",cubeStartPos2)

		while True:
			p.stepSimulation()
			time.sleep(1. / float(fps))
	finally:
		p.disconnect()
