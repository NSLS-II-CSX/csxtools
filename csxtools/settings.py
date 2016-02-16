# Define some config for the CSX beamline.
# First, lets define the FastCCD config.
detectors = {}
detectors['fccd'] = {'tag': 'fccd_image',
                     'pixel_size': (0.03, 0.03),  # mm
                     'calibrated_center': (960.0/2, 960.0/2),  # pixels
                     'dist_sample': (355.0)}  # mm

# Now lets define the reciprocal space angles which are derived
# from the motor positions.
# These are (delta, theta, gamma, chi, phi, mu)

diff_angles = ('delta', 'theta', 'gamma', -90.0, 0.0, 0.0)
