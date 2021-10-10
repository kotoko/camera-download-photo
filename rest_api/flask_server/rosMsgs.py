#!/usr/bin/env python3
from typing import List, Tuple

import roslibpy as r


class RegionOfInterest(r.Message):
	msg_type = 'sensor_msgs/RegionOfInterest'

	def __init__(self,
				x_offset: int,
				y_offset: int,
				height: int,
				width: int,
				do_rectify: bool):
		super().__init__({
			'x_offset': x_offset,
			'y_offset': y_offset,
			'height': height,
			'width': width,
			'do_rectify': do_rectify,
		})


class CameraInfo(r.Message):
	msg_type = 'sensor_msgs/CameraInfo'

	def __init__(self,
				header: r.Header,
				height: int,
				width: int,
				distortion_model: str,
				D: Tuple[float, float, float],
				K: Tuple[float, float, float, float, float, float, float, float, float],
				R: Tuple[float, float, float, float, float, float, float, float, float],
				P: Tuple[float, float, float, float, float, float, float, float, float, float, float, float],
				binning_x: int,
				binning_y: int,
				roi: RegionOfInterest):
		super().__init__({
			'header': header.data,
			'height': height,
			'width': width,
			'distortion_model': distortion_model,
			'D': D,
			'K': K,
			'R': R,
			'P': P,
			'binning_x': binning_x,
			'binning_y': binning_y,
			'roi': roi.data,
		})


class Image(r.Message):
	msg_type = 'sensor_msgs/Image'

	def __init__(self,
				header: r.Header,
				height: int,
				width: int,
				encoding: str,
				is_bigendian: int,
				step: int,
				data: List[int]):
		super().__init__({
			'header': header.data,
			'height': height,
			'width': width,
			'encoding': encoding,
			'is_bigendian': is_bigendian,
			'step': step,
			'data': data,
		})


class PointField(r.Message):
	msg_type = 'sensor_msgs/PointField'
	datatype_INT8 = 1
	datatype_UINT8 = 2
	datatype_INT16 = 3
	datatype_UINT16 = 4
	datatype_INT32 = 5
	datatype_UINT32 = 6
	datatype_FLOAT32 = 7
	datatype_FLOAT64 = 8

	def __init__(self,
				name: str,
				offset: int,
				datatype: int,
				count: int):
		super().__init__({
			'name': name,
			'offset': offset,
			'datatype': datatype,
			'count': count,
		})


class PointCloud2(r.Message):
	msg_type = 'sensor_msgs/PointCloud2'

	def __init__(self,
				header: r.Header,
				height: int,
				width: int,
				fields: List[PointField],
				is_bigendian: bool,
				point_step: int,
				row_step: int,
				data: List[int],
				is_dense: bool):
		super().__init__({
			'header': header.data,
			'height': height,
			'width': width,
			'fields': [i.data for i in fields],
			'is_bigendian': is_bigendian,
			'point_step': point_step,
			'row_step': row_step,
			'data': data,
			'is_dense': is_dense,
		})


class Extrinsics(r.Message):
	msg_type = 'realsense2_camera/Extrinsics'

	def __init__(self,
				header: r.Header,
				rotation: Tuple[float, float, float, float, float, float, float, float, float],
				translation: Tuple[float, float, float]):
		super().__init__({
			'header': header.data,
			'rotation': rotation,
			'translation': translation,
		})
