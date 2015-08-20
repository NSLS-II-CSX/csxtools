import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from subprocess import check_call
from dataportal import DataBroker as db
from dataportal import DataMuxer as dm
from dataportal import StepScan as ss
import time
import os
import sys
import h5py
import image_processor as ip
reload(ip)
from pyspec.fit import fitdata
from pyspec.fitfuncs import *
from collections import OrderedDict

class ScanProcessor():

    def __init__(self, scans=None,
              gain1_bg_scans=None,
              gain2_bg_scans=None,
              gain8_bg_scans=None):

        self.scans = scans
        self.gain1_bg_scans = gain1_bg_scans
        self.gain2_bg_scans = gain2_bg_scans
        self.gain8_bg_scans = gain8_bg_scans

        self.im_range = ''
        self.calibrate = True
        self.count_ph = False

        self.roi = None
        self.mask_image = True
        self.mask = self._get_default_mask()

        self.h5_path = '/GPFS/xf23id/scratch/vivek/h5files/'
        self.scan_h5_name = None

        self.reprocess = False
        self.reprocess_bg = False

        self.bg = None
        self.data_dict = None
        self.images = None

        self.x = 'pgm_energy'
        self.vmin = None
        self.vmax = None
        self.Title = ''
        self.x_label = ''
        self.y_label = ''

        self.fit = False
        self.fit_funcs = [linear, gauss]

        self.n_bins = 1
        self.row = 480
        self.n_rows = 1
        self.col = 490
        self.n_cols = 1

        self.processed = False

    #----------------------------- Return Attributes --------------------------

    def get_data_dict_keys(self):
        self._data_keys = self.data_dict.keys()
        return self._data_keys


    def getSIXCAngles(self):
        keys = self.data_dict.keys()

        if 'delta' in self.data_dict.keys():
            self.delta = self.data_dict['delta']
        else:
            print('\nNO delta motor values in scan! ABORT Mission!\n')
            sys.exit(0)

        if 'gamma' in self.data_dict.keys():
            self.gamma = self.data_dict['gamma']
        else:
            print('\nNO gamma motor values in scan! ABORT Mission!\n')
            sys.exit(0)

        if 'theta' in self.data_dict.keys():
            self.theta = self.data_dict['theta']
        else:
            print('\nNO theta motor values in scan! ABORT Mission!\n')
            sys.exit(0)

        if 'muR' in self.data_dict.keys():
            self.muR = self.data_dict['muR']
        else:
            self.mu = 0.0
            print('\nNO Mu motor values in scan. Using 0 for Mu values\n')

        self.chi = -90.0
        self.phi = 0.0

        sixcAngles = np.ones((len(self.delta),6))
        sixcAngles[:,0] = self.delta
        sixcAngles[:,1] = self.theta
        sixcAngles[:,2] = self.chi
        sixcAngles[:,3] = self.phi
        sixcAngles[:,4] = self.mu
        sixcAngles[:,5] = self.gamma

        return sixcAngles


    def get_energy(self):
        return self.data_dict['pgm_energy']


    def get_mean_image(self):
        return self.mean_image_all_events.mean(0)


    def get_all_images(self):
        event_keys = self._event_images_keys

        images = self.data_dict[event_keys[0]]
        for (n_event_key, event_key) in enumerate(event_keys[1:]):
            images = np.concatenate((images, self.data_dict[event_key]))

        return images


    def get_images(self):
        if not self.processed:
            self.process()

        images = ip.apply_mask(self.mean_image_all_events, self.mask)

        return images


    def get_ccd_total(self):
        # Get total counts over ROI
        return [image.sum() for image in self.mean_image_all_events]


    def get_ccd_mean(self):
        # Get average counts over ROI
        return [image.mean() for image in self.mean_image_all_events]


    def _get_scan_events(self, bg=False):
        scans = self.scans
        if bg:
            if self._bg_scans:
                scans = self._bg_scans
            else:
                print 'No background scans'
                return None

        return db.fetch_events(db[scans])


    def _get_default_mask(self):
        mask=np.zeros((960,960))
        mask[125:160,0:480] = 1
        mask[1:960,477:483] = 1

        return mask


    def _get_all_bg_scans(self):
        if (   (not self.gain1_bg_scans) and
               (not self.gain2_bg_scans) and
               (not self.gain8_bg_scans)  ):
            self._bg_scans = None

        if self.gain1_bg_scans:
            if not isinstance(self.gain1_bg_scans, list):
                self.gain1_bg_scans = [self.gain1_bg_scans]
        if self.gain2_bg_scans:
            if not isinstance(self.gain2_bg_scans, list):
                self.gain2_bg_scans = [self.gain2_bg_scans]
        if self.gain8_bg_scans:
            if not isinstance(self.gain8_bg_scans, list):
                self.gain8_bg_scans = [self.gain8_bg_scans]

        self._bg_scans = [self.gain1_bg_scans,
                         self.gain2_bg_scans,
                         self.gain8_bg_scans]


    #-----------------------------H5 File Routines ----------------------------

    def _get_h5_name(self, bg_scan=None):
        if bg_scan:
            if not isinstance(bg_scan, list): bg_scan = [bg_scan]
            if len(bg_scan) > 3:
                bg_scan = '[{0}-{1}]'.format(bg_scan[0], bg_scan[-1])
            return '{0}'.format(bg_scan)

        scans = self.scans
        if not isinstance(scans, list): scans = [self.scans]
        if len(scans) > 3:
            scans = '[{0}-{1}]'.format(scans[0], scans[-1])
        file_name = '{0}'.format(scans)

        gains = [1, 2, 8]
        bg_scans = self._bg_scans

        for gain, bg_scan in zip(gains, bg_scans):
            if bg_scan:
                if len(bg_scan) > 3:
                    bg_scan = '[{0}-{1}]'.format(bg_scan[0], bg_scan[-1])
                file_name = '{0}_gain{1}_BG_{2}'.format(
                        file_name, gain, bg_scan)

        if self.calibrate: file_name = '{0}_cal'.format(file_name)
        if self.count_ph:  file_name = '{0}_Ph'.format(file_name)

        return file_name


    def _exists_h5(self, h5_name):
        h5_file = '{0}{1}.h5'.format(self.h5_path, h5_name)
        if os.path.isfile(h5_file):
            return True

        return False


    def _write_data_to_h5(self, h5_name, data_dict, reprocess):
        h5_path = self.h5_path
        if not os.path.exists(h5_path):
            os.makedirs(h5_path)

        h5_file = '{0}{1}.h5'.format(h5_path, h5_name)
        if os.path.isfile(h5_file) & reprocess:
            check_call(["rm", "-f", h5_file])

        h5_file = h5py.File(h5_file)

        print 'Writing to {0}\n'.format(h5_file.filename)
        for key in data_dict.keys():
            h5_file.create_dataset(key, data=data_dict[key])
        h5_file.close()


    def _get_data_from_h5(self, h5_name):
        h5_path = self.h5_path
        print 'Reading from h5 file {0}{1}.h5'.format(h5_path, h5_name)
        h5_file = h5py.File('{0}{1}.h5'.format(h5_path, h5_name), 'r')

        data_dict = dict()
        for key in h5_file.keys():
            data_dict[key] = h5_file[key].value

        h5_file.close()

        return data_dict


    #-------------------------- Plotting Waterfalls ------------------------------

    def _bin_images(self, images):
        n_bins = self.n_bins

        n_images = len(images) - np.mod(len(images), n_bins)
        binned_images = images[0:n_images].reshape(n_bins, n_images / n_bins, 960, 960)
        avg_binned_images = binned_images.mean(0)

        return avg_binned_images


    def _bin_and_plot_waterfall(self, images):
        n_bins = self.n_bins
        row    = self.row
        n_rows = self.n_rows
        col    = self.col
        n_cols = self.n_cols

        avg_binned_images = self._bin_images(images)
        row_cuts = avg_binned_images[:, row:row+n_rows, :].mean(1)
        col_cuts = avg_binned_images[:, :, col:col+n_cols].mean(2)

        exp_time = self.data_dict['fccd_acquire_period'][0]

        plt.figure()
        plt.imshow(row_cuts, vmin = np.percentile(row_cuts, 20),
                             vmax = np.percentile(row_cuts, 90), aspect = 'auto')
        plt.xlabel('Columns (Horizontal cut at {0})'.format(row))
        plt.ylabel('Time ({0} x ({1} sec/frame))'.format(n_bins, exp_time))
        plt.title('Waterfall #{0} BG#{1}'.format(self.scans, self._bg_scans))
        plt.colorbar()

        plt.figure()
        plt.imshow(col_cuts, vmin = np.percentile(col_cuts, 20),
                             vmax = np.percentile(col_cuts, 90), aspect = 'auto')
        plt.xlabel('Rows (Vertical cut at {0})'.format(col))
        plt.ylabel('Time ({0} x ({1} sec/frame))'.format(n_bins, exp_time))
        plt.title('Waterfall #{0} BG#{1}'.format(self.scans, self._bg_scans))
        plt.colorbar()
        plt.show()


    def plot_waterfall(self):
        if not self.processed: self.process()

        images = self.get_all_images()
        images = ip.apply_mask(images, self.mask)

        self._bin_and_plot_waterfall(images)


    #---------------------- Data Dictionary Routines -------------------------

    def _create_data_dict(self):
        data_dict = OrderedDict()
        for key in self.scan_events.keys():
            if 'fccd_image' in key:
                continue
            data_dict[key] = self.scan_events[key]

        data_dict['scans'] = '{0}'.format(self.scans)
        if self.gain1_bg_scans:
            data_dict['gain1_bg_scans'] = '{0}'.format(self.gain1_bg_scans)
        if self.gain2_bg_scans:
            data_dict['gain2_bg_scans'] = '{0}'.format(self.gain2_bg_scans)
        if self.gain8_bg_scans:
            data_dict['gain8_bg_scans'] = '{0}'.format(self.gain8_bg_scans)

        return data_dict


    def _remove_dict_event(self, data_dict, bad_events):
        for key in data_dict.keys():
            np.delete(data_dict[key], bad_events)
        #for bad_event in reversed(bad_events):
            #for key in data_dict.keys():
                #del data_dict[key][bad_event]

        return data_dict


    #-------------------------- Process Background -------------------------

    def get_bg(self):
        gains = [1, 2, 8]
        bg_scans = self._bg_scans

        if (not bg_scans):
            self.bg = 0
            return self.bg

        h5_path = self.h5_path
        print '\n**** Processing Background Scans: {0} ****\n'.format(bg_scans)

        bg = []
        for gain, bg_scan in zip(gains, bg_scans):
            if not bg_scan:
                bg.append(0)
            else:
                print 'Gain {0} BG [{1}]'.format(gain, bg_scan)
                bg_h5_name = self._get_h5_name(bg_scan)
                if self._exists_h5(bg_h5_name) & (not self.reprocess_bg):
                    data_dict = self._get_data_from_h5(bg_h5_name)
                    bg.append(data_dict['gain{0}'.format(gain)])
                    print 'Getting data from {0}.h5\n'.format(bg_h5_name)
                else:
                    mean_bg = self._get_mean_bg(bg_scan)
                    self._write_data_to_h5(bg_h5_name,
                        {'gain{0}'.format(gain):mean_bg}, self.reprocess_bg)
                    bg.append(mean_bg)

        self.bg = bg
        print '\n**** Background Processed ****\n'


    def _get_mean_bg(self, bg_scans):
        scan_events = ss[bg_scans]
        for n_event, event_images in enumerate(scan_events.fccd_image_lightfield):
            if n_event == 0:
                images_data = event_images[1:]
            else:
                images_data =  np.concatenate((images_data, event_images[1:]))
        print 'Number of images: {0}'.format(len(images_data))

        images_data = ip.mask_bad_pixels(images_data)
        images = ip.get_image_bits(images_data)
        images_mean = images.mean(0)

        return images_mean


    #------------------------- Extract and Process Scans -------------------------

    def get_scan_data(self):
        # import image of target for BG subtraction
        scan_events = ss[self.scans]
        self.scan_events = scan_events
        data_dict = self._create_data_dict()

        bad_events = []

        print '\n***** Processing Scans: {0} *****\n'.format(self.scans)
        for n_event, event_images in enumerate(scan_events.fccd_image_lightfield):
            if len(event_images) < 2:
                print 'No image data for event number {0} in scan'.format(n_event+1)
                bad_events.append(n_event-1)
                continue

            n_event_images = len(event_images) - 1
            print 'Event {0} - {1} images'.format(n_event+1, n_event_images)

            processed_event_images = np.zeros((n_event_images,960,960))
            for n_image, image_data in enumerate(event_images[1:]):
                processed_image = ip.process_image_data(image_data, bg=self.bg,
                        calibrate=self.calibrate, count_ph=self.count_ph)
                processed_event_images[n_image] = processed_image

            data_dict['event_{0}_images'.format(n_event+1)] = processed_event_images

        print '\n**** Scan Processed ****\n'

        self.data_dict = data_dict


    #--------------------- Get Data for Specified Image Range -----------------------

    def get_im_range(self):
        data_dict = self.data_dict
        if not self.im_range:
            self.im_range = [0, len(data_dict['event_1_images'])]
        im_range = self.im_range

        if (len(im_range) == 2) and (im_range[1] < 1):
            im_range[1] = len(data_dict['event_1_images']) + im_range[1]

        self._event_images_keys = [key for key in data_dict.keys()
                if '_images' in key]

        key = 'mean_image_all_events{0}'.format(im_range)
        if key not in data_dict.keys():
            all_keys = self._event_images_keys
            mean_image_all_events = np.zeros((len(all_keys),960,960))

            for n_event, event_key in enumerate(all_keys):
                mean_image_all_events[n_event] = ( data_dict[event_key]
                        [im_range[0]:im_range[1]].mean(0) )

            self.data_dict[key] = mean_image_all_events
            self._write_data_to_h5(self.scan_h5_name, self.data_dict, self.reprocess)

        self.mean_image_all_events = self.data_dict[key]


    #------------------------------ Process Data ----------------------------

    def process(self):
        t1 = time.time()

        self._get_all_bg_scans()
        self.scan_h5_name = self._get_h5_name()

        if self._exists_h5(self.scan_h5_name) & (not self.reprocess):
            print '\nProcessed data found'
            self.data_dict = self._get_data_from_h5(self.scan_h5_name)
        else:
            self.get_bg()
            self.get_scan_data()

        self.get_im_range()

        if self.mask_image:
            self.mean_image_all_events = ip.apply_mask(self.mean_image_all_events,
                    mask=self.mask)

        if self.roi:
            self.mean_image_all_events = ip.get_roi(self.mean_image_all_events,
                    self.roi)

        self.processed = True
        print '\nProcessing time: {0}'.format(time.time() - t1)

        self.angles = self.getSIXCAngles()
        self.images = self.get_images()


    #--------------------------------- Plot Data ------------------------------

    def show(self):
        if not self.processed: self.process()

        self.image_plot(self.get_mean_image())

        if len(self.mean_image_all_events) > 5:
            self.line_plot()
        plt.show()


    #--------------------------- Plotting Routines ----------------------------

    def line_plot(self):
        Title = self.Title + ' #{0}'.format(self.scans)
        if self._bg_scans: Title = Title + ' BG#{0}'.format(self._bg_scans)

        x_data = self.data_dict[self.x]
        y_data = self.get_ccd_total()

        fig, ax = plt.subplots()
        ax.plot(x_data, y_data, 'bo')
        if self.fit:
            fitdata(self.fit_funcs)
        else:
            ax.plot(x_data, y_data, 'b-')

        if self.x_label == '': self.x_label = self.x
        ax.set_xlabel(self.x_label)

        if self.y_label == '': self.y_label = 'CCD ROI Total Counts'
        ax.set_ylabel(self.y_label)

        ax.set_title(Title)

        return [x_data, y_data]


    def image_plot(self, images):
        Title = self.Title + ' #{0}'.format(self.scans)
        if self._bg_scans: Title = Title + ' BG#{0}'.format(self._bg_scans)

        if not isinstance(images, list): images = [images]

        for image in images:
            fig, ax = plt.subplots()
            if not self.vmin: self.vmin = 0.75*np.median(image)
            if not self.vmax: self.vmax = 1.25*np.median(image)
            im = ax.imshow(image, vmin=self.vmin, vmax=self.vmax)
            ax.set_title(Title)
            plt.colorbar(im)


#-------------------------- Extract and Process Data -------------------------



def plot_scan(scans, bg_scans=None, x='theta', roi=None, reprocess=False,
        Title='', x_label='', y_label=''):
    data, images = plot_ccd(scans, x=x, roi=roi, calibrate=True,
            reprocess=reprocess)#, plot_data=False)
    if bg_scans:
        data, images_bg = plot_ccd(bg_scans, x=x, roi=roi, calibrate=True,
                reprocess=reprocess)#, plot_data=False)
        images = [(image - image_bg) for image, image_bg
                in zip(images, images_bg)]

    data_y = [image.mean() for image in images]
    #if x in data.keys(): data_x = data[x]
    #else: data_x = range(len(data_y))
    data_x = data['x']

    line_plot(data_x, data_y, x,
            scans, bg_scans=bg_scans, Title=Title,
            x_label=x_label, y_label=y_label)
    plt.show()

    return data_x, data_y


if __name__ == '__main__':
    # Extracting and processing data
    roi = [385, 400, 460, 475]
    plot_ccd(10835, bg_scans=10836)
