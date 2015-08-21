import numpy as np
import matplotlib.pyplot as plt
import os
import numpy.ma as ma

class image_processor():
    def __init__(self, images=None):
        """ Initialize
        """
        if images is not None:
            self.images = images


def apply_flat_field_corr(images, exp_time='10_sec_each_col'):
    ff_path = '/GPFS/xf23id/scratch/vivek/flat_field/'
    flat_field_image_file = '{0}ff_{1}.npy'.format(ff_path, exp_time)
    if os.path.exists(flat_field_image_file):
        flat_field_corr = np.load(flat_field_image_file)
        images = images/flat_field_corr
    else:
        print 'No flat field image data... No correction applied'

    return images


def apply_mask(images, mask=np.zeros(0)):
    if len(mask) == 0:
        mask=np.zeros((960,960))
        mask[125:160,0:480] = 1
        mask[1:960,477:483] = 1

    if not isinstance(images, list):
        if images.ndim == 2:
            return ma.masked_array(images, mask)
        elif images.ndim == 3:
            if mask.ndim == 3:
                mask_3d = mask
            else:
                mask_3d = np.zeros((len(images),960,960))
                for i in range(len(images)): mask_3d[i] = mask
            return ma.masked_array(images, mask_3d)

    masked_images = [ma.masked_array(image, mask) for image in images]

    return masked_images


def get_roi(images, roi):
    if not isinstance(images,list):
        if images.ndim == 2:
            images = [images]

    images_roi = [image[roi[0]:roi[1], roi[2]:roi[3]] for image in images]

    return images_roi


def get_image_bits(image):
    ImgBin = int('0b0001111111111111',2)
    image = (image & ImgBin).astype(float)

    return image


def mask_bad_pixels(images):
    #packet drop
    P = int('0b0010000000000000',2)
    bad_pixel_mat = (images & P) == P
    if bad_pixel_mat.sum() > 0:
        print 'Number of bad pixels: {0}'.format(bad_pixel_mat.sum())

    return apply_mask(images, bad_pixel_mat)


def get_gain_matrix(images):
    # Gains bits
    G1 = int('0b1100000000000000',2)
    G2 = int('0b1000000000000000',2)
    G8 = int('0b0000000000000000',2)

    gain1_mat = (images & G1) == G1
    gain2_mat = (images & G1) == G2
    gain8_mat = (images & G1) == G8

    return [gain1_mat, gain2_mat, gain8_mat]


def adjust_gain(images, gain_matrices):
    if not isinstance(images, list): images = [images, images, images]
    gain_adjusted_image = (gain_matrices[0] * images[0] * 8 +
                           gain_matrices[1] * images[1] * 4 +
                           gain_matrices[2] * images[2] * 1)

    return gain_adjusted_image


def process_image_data(image_data, bg=None, calibrate=False, count_ph=False):
    if not bg: bg = 0

    # Mask Bad Pixeld
    image_data = mask_bad_pixels(image_data)

    # Get gain matrices
    gain_matrices = get_gain_matrix(image_data)

    # Get image bits
    raw_images = get_image_bits(image_data)

    # Apply gain correction
    gain_adjusted_images = adjust_gain(raw_images, gain_matrices)
    gain_adjusted_bg    = adjust_gain(bg, gain_matrices)

    # Dark BG subtraction
    processed_images = np.fliplr((gain_adjusted_images - gain_adjusted_bg).T)

    # Apply flat field correction
    if calibrate:
        processed_images = apply_flat_field_corr(processed_images)

    if count_ph:
        print 'Image #{0}'.format(n_good_images+1)
        n_photons, processed_images = count_photons(processed_images,
                threshold_low=None, threshold_high=None,
                photon_eV=931, eV_per_ADU=25,
                grid_size=3, n_pixels_sum=5)

    return processed_images


def count_photons(image, threshold_low=None, threshold_high=None,
                  photon_eV=931, eV_per_ADU=25,
                  grid_size=3, n_pixels_sum=5):

    if not threshold_low:
        threshold_low  = 0.5 * (photon_eV / eV_per_ADU)
    if not threshold_high:
        threshold_high = 1.0 * (photon_eV / eV_per_ADU)
    #print 'ADU Threshold: [{0}, {1}]'.format(threshold_low, threshold_high)

    cleaned_image = np.zeros(image.shape)
    n_rows, n_cols = image.shape

    # Get all pixels between threshold value
    bright_pixels = np.where( (image > threshold_low) & (image < threshold_high) )
    print 'Number of bright pixels: {0}'.format(len(bright_pixels[0]))

    if len(bright_pixels[0]) == 0:
        print 'No photons in image... Turn the light ON!!!'
        return 0, cleaned_image

    ADU_per_photon = photon_eV/eV_per_ADU
    #print 'ADU_per_photon = {0:.2f}'.format(ADU_per_photon)
    n_photons = 0

    for row, col in zip(bright_pixels[0], bright_pixels[1]):
        # Define ROI around each bright pixel
        grid_roi = [max(row - (grid_size-1)/2, 0), min(row + (grid_size-1)/2, n_rows-1) + 1,
                    max(col - (grid_size-1)/2, 0), min(col + (grid_size-1)/2, n_cols-1) + 1]
        grid_image = image[grid_roi[0]:grid_roi[1], grid_roi[2]:grid_roi[3]]

        # Find brightest (seed) pixel in ROI and define new seed ROI (3x3)
        seed_pixel_in_grid  = np.unravel_index(grid_image.argmax(), grid_image.shape)

        # Convert to full image coordinates
        seed_row, seed_col = [seed_pixel_in_grid[0] + grid_roi[0],
                              seed_pixel_in_grid[1] + grid_roi[2]]

        seed_grid_roi = [max(seed_row - 1, 0), min(seed_row + 1, n_rows-1) + 1,
                         max(seed_col - 1, 0), min(seed_col + 1, n_cols-1) + 1]
        seed_grid_image = image[seed_grid_roi[0]:seed_grid_roi[1],
                                seed_grid_roi[2]:seed_grid_roi[3]]

        # Find sum over 5 brightest pixels in seed ROI
        max_n_pixels = np.argsort(seed_grid_image.ravel())[::-1][0:n_pixels_sum]
        sum_max_n_pixels = np.sort(seed_grid_image.ravel()[max_n_pixels]).sum()

        # Compare sum with incident photon energy
        if ((sum_max_n_pixels > 0.85*ADU_per_photon) &
            (sum_max_n_pixels < 1.15*ADU_per_photon)):
            # Write each pixel intensity into clean image
            for pixel in max_n_pixels:
                pixel_row, pixel_col = np.unravel_index(pixel, seed_grid_image.shape)
                # Again convert to full image coordinates
                pixel_row = pixel_row + seed_grid_roi[0]
                pixel_col = pixel_col + seed_grid_roi[2]

                # Write to clean image
                cleaned_image[pixel_row, pixel_col] = image[pixel_row, pixel_col]

                # Set pixel values to 0 in original image
                image[pixel_row, pixel_col] = 0
                n_photons += 1

    print 'Number of photon events: {0}\n'.format(n_photons)
    return n_photons, cleaned_image


if __name__ == "__main__":
    plt.close('all')

    path = '/Users/v/Research/Tardis/Fast CCD/Fe55 Images/'
    image = plt.imread(path + 'fastCCD-Example-Fe55-Image.tif')

    plt.figure()
    plt.imshow(image, vmin=3700, vmax=4000)
    plt.colorbar()

    calibrated_image = intercalibrate_columns(image)
    calibrated_image_roi = get_roi(calibrated_image, [100,100,700,300])

    plt.figure()
    plt.imshow(calibrated_image_roi, vmin=-100, vmax=50)
    plt.colorbar()

    n_photons, cleaned_image = count_photons(calibrated_image_roi)

    plt.figure()
    plt.imshow(cleaned_image, vmin=-100, vmax=50)
    plt.colorbar()

    plt.show()
