#!/usr/bin/env python3

import os
import toml
import tempfile
import shutil


configPath = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.toml'))
defaultConfig = '''
[camera]
width = 1280
height = 720

[worker_ros]
host = "127.0.0.1"
port = 9090
topic_color = "/camera/color/image_raw"
topic_depth = "/camera/depth/image_rect_raw"

[worker_opencv]
device = 0

[worker_pybullet]
mode = "tcp"
host = "127.0.0.1"
port = 6667
eye_position = [0, 0, 3]
eye_up_vector = [0, 1, 0]
target_position = [0, 0, 0]
fov = 45.0
aspect = 1.0
near_distance = 0.1
far_distance = 3.1

[upload_ros]
host = "127.0.0.1"
port = 9090
topic_color = "/fake_camera/color"
topic_depth = "/fake_camera/depth"
'''


# Zapisz podaną konfigurację do pliku
def saveConfig(cfg):
	with tempfile.NamedTemporaryFile('wt') as tmp:
		toml.dump(cfg, tmp)
		tmp.flush()

		shutil.copyfile(tmp.name, configPath)


# Stwórz plik z przykładową domyślną konfiguracją
def genDefault():
	cfg = toml.loads(defaultConfig)
	saveConfig(cfg)


# Odczytaj całą konfigurację z pliku
def getConfig():
	if not os.path.exists(configPath):
		genDefault()

	cfg = toml.load(configPath)

	return cfg
