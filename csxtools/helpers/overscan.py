import numpy as np

def _extract_from_fccdwithOS_osdata(images, os_cols, data_cols):
    if len(images.shape) !=4:
        print(f'Input images should be 4D.')
        raise
    #print(images.shape)
    points, frames, total_cols, horz_pix = images.shape
    super_cols = int(total_cols / (os_cols+data_cols))
    os_cols_data =  np.zeros((os_cols,   points, frames, super_cols, horz_pix), )
    
    #print(f'{os_cols_data.shape=}')
    

    for i in range(os_cols):
        #print(i)
        #print(f'\t{os_cols+data_cols}')
        os_cols_data[i] = images[:, :, i::os_cols+data_cols, :]
        
    return os_cols_data

# def extract_from_fccdwithOS_photondata(images, os_cols, data_cols):
#     if len(images.shape) !=4:
#         print(f'Input images should be 4D.')
#         raise
#     points, frames, total_cols, _ = images.shape
#     super_cols = int(total_cols / (os_cols+data_cols))
#     data_cols_data =  np.zeros((data_cols,   points, frames, super_cols, rows), )

#     for i in range(data_cols):
#         data_cols_data[i] = ar_images[:, :, i+os_cols::os_cols+data_cols, :]
        
#     return data_cols_data

def _make_os_correction_data(os_data, os_cols, data_cols, images_data_shape, ):
    #print(f'{os_data.shape=}')
    if len(images_data_shape) !=4 and len(os_data.shape) != 4:
        print(f'Input images should be 4D.')
        raise
    points, frames, total_cols, horz_pix = images_data_shape
    super_cols = int(total_cols / (os_cols+data_cols))
    vert_pix = super_cols * data_cols
    
    os_data_for_broadcast = np.zeros((points, frames, vert_pix , horz_pix  ))
    #print(f'{os_data_for_broadcast.shape=}')

    for i in range(super_cols):
        #print(i)
        temp = os_data[:,:,i, :].reshape(points, frames, 1, horz_pix)
        os_supercol_data = np.broadcast_to(temp, (points, frames, data_cols, horz_pix))
        #print(f'\t{os_supercol_data=}')
        #print(f'\t{os_supercol_data.shape=}')
        start, stop = i*(data_cols), data_cols*(i+1)
        #print(f'\t{start} : {stop}')
        os_data_for_broadcast[:,:, start : stop , :] = os_supercol_data
        
    return os_data_for_broadcast
    
def _drop_os_data(images, os_cols, data_cols):
    if len(images.shape) !=4:
        print(f'Input images should be 4D.')
        raise
    points, frames, total_cols, horz_pix = images.shape
    super_cols = int(total_cols / (os_cols+data_cols))
    vert_pix = super_cols * data_cols
    images_no_os =  np.zeros((  points, frames, vert_pix, horz_pix) )
    #print(f'{images_no_os.shape=}')
    
    for i in range(super_cols):
        #print(i)
        start_extract, stop_extract = i*(data_cols+os_cols)+os_cols, (data_cols+os_cols)*(i+1)#+os_cols
        #print(f'\tOUT OF {start_extract}:{stop_extract}')
        temp = images[:,:,start_extract:stop_extract, :]
        #print(f'\t{temp.shape}')
        start_in, stop_in = i*data_cols, i*data_cols+data_cols
        #print(f'\tINTO {start_in}:{stop_in}')
        #target = images_no_os[:,:, start_in : stop_in , :]
        #print(f'\t{target.shape}')
        images_no_os[:,:, start_in : stop_in , :] = temp
        
    #print(f'{images_no_os.shape=}')
        
    return images_no_os

def _make_left_right(images):
    horz_pix = images.shape[-1]
    imgs_left = np.flip(np.copy(images[:,:,:,0:int(horz_pix/2)]))
    imgs_right = np.copy(images[:,:,:,int(horz_pix/2):horz_pix])
    
    return imgs_left, imgs_right

#def _make_whole_from_left_right(images_left, images_right):
#    images = np.concatenate((np.flip(images_left), images_right), axis=-1)
    

def get_os_correction_images(images, os_cols=2, data_cols=10, os_mean=True, os_single_col=None):

    if os_mean == 'False' and os_single_col is None:
        print('select nth column if not using mean')
        raise
        
    images_left, images_right =  _make_left_right(images) 
    #print(images_left.shape, images_right.shape)
    
    os_extract_left = _extract_from_fccdwithOS_osdata(images_left, os_cols, data_cols)
    os_extract_right = _extract_from_fccdwithOS_osdata(images_left, os_cols, data_cols)
    
    #print(os_extract_left.shape, os_extract_right.shape)
    if os_mean:
        os_imgs_left = _make_os_correction_data(np.mean(os_extract_left, axis=0), 
                                                os_cols, data_cols, images_left.shape )
        os_imgs_right = _make_os_correction_data(np.mean(os_extract_right, axis=0), 
                                                 os_cols, data_cols, images_right.shape )
    else:
        os_imgs_left = _make_os_correction_data(os_extract_left[os_single_col], 
                                                os_cols, data_cols, images_left.shape )
        os_single_col = int(not os_single_col )#preserving readout order, not location in flipped array
        os_imgs_right = _make_os_correction_data(s_extract_right[os_single_col ], 
                                                 os_cols, data_cols, images_right.shape )
        
    #print(os_imgs_left.shape, os_imgs_right.shape)
    os_imgs = np.concatenate((np.flip(os_imgs_left), os_imgs_right), axis=-1)
    
    #print(os_imgs.shape)
    
    return os_imgs
    
    
def get_os_dropped_images(images, os_cols=2, data_cols=10):
    imgs_left, imgs_right =  _make_left_right(images)
    
    imgs_left_no_os = _drop_os_data(imgs_left, os_cols, data_cols)
    imgs_right_no_os = _drop_os_data(imgs_right, os_cols, data_cols)
    
    #print(f'{imgs_left_no_os.shape=}')
    
    images = np.concatenate((np.flip(imgs_left_no_os), imgs_right_no_os), axis=-1)
    #images = _make_whole_from_left_right(imgs_left_no_os, imgs_right_no_os)
    #print(f'{images.shape=}')
    
    return images
    
    
    
