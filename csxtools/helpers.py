import pandas
from collections import namedtuple

#from csxtools.image import rotate90, stackmean
from csxtools.utils import  get_fastccd_images

from csxtools.image_correction_overscan import get_os_correction_images, get_os_dropped_images

import logging
logger = logging.getLogger(__name__)

  

def find_possible_darks(header, dark_gain, search_time, return_debug_info,exposure_time_tolerance = 0.002):
    darks_possible ={'scan':[],'exp_time':[], 'delta_time':[] }
    start_time = header.start["time"]
    stop_time = header.stop["time"]
    if header.stop["exit_status"] != 'abort': #because the key is missing from descriptors, was never recorded
    #try:
        exp_time = header.descriptors[0]['configuration']['fccd']['data']['fccd_cam_acquire_time']
        #except:
            #print(header.start["scan_id"])
            #raise

    
    hhs = db(since = start_time - search_time, until = start_time, **{'fccd.image': 'dark'},  **{'fccd.gain': dark_gain})
    data = [[h.start["scan_id"], h.descriptors[0]['configuration']['fccd']['data']['fccd_cam_acquire_time'],
                                          start_time-h.start['time']] for h in hhs if getattr(h, 'stop', {}).get('exit_status', 'not done') == 'success']
            
    hhs = db(since = stop_time, until =  stop_time + search_time, **{'fccd.image': 'dark'},  **{'fccd.gain': dark_gain})
    data.extend( [[h.start["scan_id"], h.descriptors[0]['configuration']['fccd']['data']['fccd_cam_acquire_time'],
                                          h.stop['time']-stop_time] for h in hhs if getattr(h, 'stop', {}).get('exit_status', 'not done') == 'success'])
    data=np.array(data)
    #print(data)
    for i,k in enumerate(darks_possible.keys()):
        try:
            darks_possible[k] = data[:,i]

        except IndexError:
            darks_possible[k] = None
            return darks_possible
        
    darks_possible = pandas.DataFrame(darks_possible)
    #clean up if exposure times are not within exp_time_tolerance seconds
    darks_possible = darks_possible[darks_possible['exp_time'].apply(np.isclose, b=exp_time, atol=exposure_time_tolerance) == True]

    
    return darks_possible

def get_dark_near(header, dark_gain = 'auto', search_time=30*60, return_debug_info = False):
    """ Find and extract the most relevant dark image (relevant in time and gain setting) for a given scan.
    header      :  databroker header of blueksy scan
    dark_gain   :  string  
                   match dark gain settings as described in the start document ('auto', 'x2', 'x1')
    search_time :  int or float 
                   time in seconds before (after) the start (stop) document timestamps
    """
    
    darks_possible = find_possible_darks(header, dark_gain, search_time, return_debug_info)
    #print( darks_possible )
    try:
        dark = int(darks_possible.sort_values(by='delta_time').reset_index()['scan'][0])
    except:
        dark = None
        return None

    if return_debug_info:
        return db[dark], darks_possible
    else:
        return db[dark]

def get_dark_near_all(header, **kwargs):
    d8,d2,d1 = (get_dark_near(header,dark_gain= dg, **kwargs) for dg in ['auto','x2','x1'])
    return d8,d2,d1    



def get_fccd_roi(header, roi_number):
    """Returns named tuple to describe AreaDetector's ROI plugin configuraiton for STATS plugin computation for a given
    databroker header. The outputs will only be correct for a correctly cropped image matching the AreaDetector setup.
    Parameters
    ----------
    header : databroker header
    roi_number : int
                 nth ROI.  Typically 1-4 are configurable and 5 is the entire sensor.
    Returns
    -------
    named tuple
      start_x : int, horizontal starting pixel from left (using output of get_fastccd_images())
      size_x  : int, horizontal bin size for ROI 
      start_y : int, vertical starting pixel from top (using output of get_fastccd_images())
      size_y  : int, vertical bin size for ROI
      name    : string, name assigned by user in ROI (optional)
        
    """
    config = header.descriptors[0]['configuration']['fccd']['data']
    if config  == {}:                    #prior to mid 2017
        x_start, x_size, y_start, y_size = None
        logger.warning('Meta data does not exist.')
    #elif config[f'fccd_stats{roi_number}_compute_statistics'] == 'Yes':
    else:
        x_start = config[f'fccd_roi{roi_number}_min_xyz_min_x']
        x_size  = config[f'fccd_roi{roi_number}_size_x']
        y_start = config[f'fccd_roi{roi_number}_min_xyz_min_y']
        y_size  = config[f'fccd_roi{roi_number}_size_y']
        name    = config[f'fccd_roi{roi_number}_name_']
        
        
    FCCDroi = namedtuple('FCCDroi', ['start_x', 'size_x', 'start_y', 'size_y', 'name'])
    return FCCDroi(x_start, x_size, y_start, y_size, name)

def get_fccd_exp(header):
    """Returns named tuple of exposure time, exposure period and number of images per "point" for a databroker header. 
    Parameters
    ----------
    header : databroker header
    
    Returns
    -------
    named tuple
      exp_time    : float, exposure time (photon integration) of each image in seconds
      exp_period  : float, exposure period time in seconds.  the time between consecutive frames for a single "point". 
                    Most often used to convert XPCS lag_step (or delays) to "time" from "frames"
      num_images  : int, number of images per "point".
        
    """
    config = header.descriptors[0]['configuration']['fccd']['data']
    if config  == {}:                    #prior to mid 2017
        exp_t = header.table().get('fccd_acquire_time')[1]
        exp_p = header.table().get('fccd_acquire_period')[1]
        exp_im = header.table().get('fccd_num_images')[1]
    else:                                #After mid 2017
        exp_t = config['fccd_cam_acquire_time']
        exp_p = config['fccd_cam_acquire_period']
        exp_im = config['fccd_cam_num_images']
        
    FCCDexp = namedtuple('FCCDexposure_config', ['exp_time' , 'exp_period', 'num_images'])
    return FCCDexp(exp_t, exp_p, exp_im)

def get_fccd_pixel_readout(header):
    """Returns named tuple of details needed to properly concatenate the fccd images. 
    Parameters
    ----------
    header : databroker header
    
    Returns
    -------
    named tuple
      overscan_cols : int, confgured by timing file for the number of virtual columns for dark current noise
      rows          : int, number of raws for framestore versus nonframestore mode, as instituted by FCCD plugin for EPICS AreaDectector
      row_offset    : int, unused virtual pixels to be removed, as instituted by FCCD plugin for EPICS AreaDectector
        
    """
    config = header.descriptors[0]['configuration']['fccd']['data']
    try:
        overscan_cols = config['fccd_cam_overscan_cols'] #this is hardware config
    except:
        overscan_cols = 'unknown' #can code using tiled to infer by Xarray shape; test setting to None
    try:
        rows = config['fccd_fccd1_rows']
        row_offset = config['fccd_fccd1_row_offset']
    except:
        rows = 'unknown'       ##need to rely on hardcoded concatenation ; test setting to None
        row_offset = 'unknown' ##need to rely on hardcoded concatenation ; test setting to None
    
    FCCDconcat = namedtuple('FCCDconcat', ['overscan_cols' , 'rows', 'row_offset'])
    return FCCDconcat(overscan_cols, rows, row_offset)

def get_fastccd_images_sized(header, dark_headers=None, flat=None, auto_concat = True, auto_overscan=True, return_overscan_array = False, drop_overscan=True):
    """Normalazied images with proper contatenation and overscan data by calling get_fastccd_images
    Parameters
    ----------
    light_header : databorker header  

    dark_headers : tuple of 3 databroker headers , optional
        These headers are the dark images. The tuple should be formed
        from the dark image sets for the Gain 8, Gain 2 and Gain 1
        (most sensitive to least sensitive) settings. If a set is not
        avaliable then ``None`` can be entered.

    flat : array_like
        Array to use for the flatfield correction. This should be a 2D
        array sized as the last two dimensions of the image stack. 
        See csxtools.utilities.get_flatfield() and use plan_name count_flatfield.
        
    auto_concat : Boolean
        True to remove un-needed vertical pixels
    
    auto_overscan : Boolean
        True to correct images with overscan data and remove overscan data
        from the array
        
    return_overscan_array : Boolean
        False to not return the overscan data as a seperate array (broadcastable)

    drop_overscan: Boolean
        If auto_overscan False, choose to keep or drop the overscan data from 
        the returned data images
        
    
        
    Returns
    -------
        Normalized fastccd data that has been properply concatenated and any overscan data
                    
    The new get_fastccd_images will always return the array (4D) so there is no need to use the get_images_to_3D or 4D.  We will just do 4D until official csxtools PR merge"""
    
    
    #print('Processing scan {}'.format(header['start']['scan_id']))
    images = get_fastccd_images(header, dark_headers, flat=flat)
    ###TODO write if statement for image shape if the output is an array (future csxtools upgrade), then there is no need for next 2 lines
    stack = get_images_to_4D(images)
    images =stack
    total_rows = images.shape[-1] #TODO add to descriptors for image output saving?, but dan must have it somewhere in the handler.
    
    fccd_concat_params = get_fccd_pixel_readout(header)
    
    #### SEE IF OVERSCAN WAS ENABLED
    if fccd_concat_params.overscan_cols != 2:
        images_have_overscan = None
        #TODO future elif to look at shape of data (1132 pix, not 960) 
    else:
        images_have_overscan = True #TODO later, go back and add code later to capture the overscan data
    
    ### make FCCD images the correct shape (except for overscan)    
    if auto_concat:
        if fccd_concat_params.rows != 'unknown': #goback and change to None when testing
            leftstart = fccd_concat_params.row_offset+1 ##TODO make sure it works for non-framestore (is it 'fccd_cam_image_mode'=2?)
            leftend = fccd_concat_params.rows*1 +fccd_concat_params.row_offset
            rightstart = total_rows - fccd_concat_params.row_offset -fccd_concat_params.rows
            rightend = total_rows - fccd_concat_params.row_offset + 1
            print(leftstart, leftend, rightstart, rightend) #TODO add this to verbose warnings level
        else:
            print('Concatenating images based on hard-coded values')#make this normal warning statement
            logging.warning('Concatenating images based on hard-coded values')
            auto_concat =  False
            if total_rows > 1001:   ##because non-framestore 
                print('images are larger than 960 pixels, first image shape is' , images[0,0].shape)#make this normal warning statement
                logging.warning('images are larger than 960 pixels, first image shape is' , images[0,0].shape)
                leftstart = 486
                leftend = 966
                rightstart =  1034
                rightstart =  1514
            elif total_rows == 1000:
                leftstart = 7
                leftend = 486
                rightstart =  514
                rightstart =  995
        images = np.concatenate((images[:,:,:,leftstart : leftend],images[:,:,:, rightstart:rightend]),axis=3)
    
    ### deal with overscan if present
    if auto_overscan and images_have_overscan:
        overscan_data = get_os_correction_images(images) ## this is "broadcastable" with images
        print(overscan_data.shape, 'os data returned in same shape as images should be')
        images = get_os_dropped_images(np.copy(images)) 
        print(images.shape, 'os dropped and substracting overscan')
        
        images = images - overscan_data
        logging.warning('overscan not well tested - unsure if overscan correction improves quality of data')
                
    
    elif auto_overscan == False and images_have_overscan and drop_overscan:
        images = get_os_dropped_images(np.copy(images)) 
        print(images.shape,'only dropping os from images')
    
    elif auto_overscan == False and images_have_overscan and drop_overscan == False:
        print(images.shape,'retaining os in returned data images')
    
    if return_overscan_array:
        return images, overscan_data
    else:
        return images
        
        

def convert_photons(images_input, energy, ADU_930 = 30, quantize_photons = True, make_int_strip_nan= True, round_to_tens=True):
    """Convert ADU to photons based on incident beamline energy.  FCCD #2 found to be ~30 ADU fro 930eV (ideally 25 ADU). 
    Quantized to photons may be problematic in the realm of 4 photon events per pixel. We should add some histogram information.
    
    Parameters
    ----------
    images_input : numpy array
    energy       : float, incident photon energy
    
    quantize_photons   : rounds pixel values to one's place. returns float or int based on make_int_strip_nan
    make_int_strip_nan : converts rounded pixel values to integers and then NaNs are very near zero
   
    Returns
    -------
    images_output : numpy array converted to photons
    
    #TODO seems to retain nan's need to use a mask to prevent pixels with nan
    #TODO do more testing to make sure rounding is alway appropriate scheme (or at all)
    #TODO it seems that simple rounding creates +/- 4 photon error around "zero" photons 
    """
    if round_to_tens:
        ADUpPH = round(ADU_930*np.nanmean(energy)/930, -1) #TODO should be ok and more consistent, but need to check with energyscans,
    else:
        ADUpPH = round(ADU_930*np.nanmean(energy)/930, 2)
    images_input = images_input / ADUpPH
    if quantize_photons == True:
        if make_int_strip_nan == True:
            images_output = np.round(images_input).astype('int')
        else:        
            images_output = np.round(images_input)
    else: 
        images_output = images_input
    return images_output, energy, ADU_930, ADUpPH