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
		husky = p.loadURDF("husky/husky.urdf", [0.290388, 0.329902, -0.310270], [0.002328, -0.000984, 0.996491, 0.083659])

		while True:
			p.stepSimulation()
			time.sleep(1. / float(fps))
	finally:
		p.disconnect()
