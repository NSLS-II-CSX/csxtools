detectors = {}
detectors['fccd'] = {}
detectors['fccd']['tag'] = 'fccd_image'
detectors['fccd']['size'] = (960, 960)
detectors['fccd']['pixel_size'] = (0.03, 0.03)  # mm
detectors['fccd']['calib_center'] = (960-280, 480)
detectors['fccd']['dist_sample'] = 340.0

diff_angles = {}
diff_angles['names'] = ('delta', 'theta', None, None, None, 'gamma')
diff_angles['defaults'] = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
