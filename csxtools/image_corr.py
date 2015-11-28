import numpy as np
from itertools import chain
import uuid
import time as ttime
from metadatastore.commands import get_events_generator
from databroker.databroker import fill_event
from databroker.pivot import pivot_timeseries, zip_events, reset_time



def subtract_background(image, dark_image, gain=(1, 4, 8)):
    gain_mask_8 = (image & 0xC000) == 0xC000
    gain_mask_4 = (image & 0xC000) == 0x8000
    gain_mask_1 = (image & 0xC000) == 0x0000
    error_mask  = (image & 0xC000) == 0x2000

    image = image & 0x1FFF

    cor_image = image.astype(np.float16)
    cor_image -= gain_mask_8 * dark_image[2]
    cor_image -= gain_mask_4 * dark_image[1]
    cor_image -= gain_mask_1 * dark_image[0]

    gain_image = (gain_mask_8 * gain[2])
    gain_image += (gain_mask_4 * gain[1])
    gain_image += (gain_mask_1 * gain[0])

    return (cor_image * gain_image), gain_image, error_mask

def correct_events(evs, data_key, dark_images, drop_raw=False):
    out_data_key = data_key + '_corrected'
    ev0 = next(evs)
    new_desc = dict(ev0['descriptor'])
    new_desc['data_keys'][out_data_key] = dict(new_desc['data_keys'][data_key])
    new_desc['data_keys'][out_data_key]['source'] = 'subtract_background'
    new_desc['uid'] = uuid.uuid4()
    if drop_raw:
        new_desc['data_keys'].pop(data_key)
    for ev in chain((ev0, ), evs):
        new_ev = {'uid': str(uuid.uuid4()),
                 'time': ttime.time(),
                 'descriptor': new_desc,
                 'seq_no': ev['seq_no'],
                 'data': dict(ev['data']),
                 'timestamps': dict(ev['timestamps'])}
        corr, gain_img, err_mask = subtract_background(ev['data'][data_key], dark_images)
        new_ev['data'][out_data_key] = corr
        new_ev['timestamps'][out_data_key] = ttime.time()
        if drop_raw:
            new_ev['data'].pop(data_key)
            new_ev['timestamps'].pop(data_key)
        yield new_ev


def clean_images(header, pivot_key, timesource_key, dark_images=None, static_keys=None):
    if static_keys is None:
        static_keys = ['sx', 'sy', 'temp_a', 'temp_b', 'sz']
    # sort out which descriptor has the key we want to pivot on
    pv_desc = [d for d in header['descriptors'] if pivot_key in d['data_keys']][0]
    # sort out which descriptor has the key that we want to zip with to get time stamps
    ts_desc = [d for d in header['descriptors'] if timesource_key in d['data_keys']][0]

    ts_events = get_events_generator(ts_desc)
    pv_events = get_events_generator(pv_desc)
    # fill_event works in place, sillyness to work around that
    pv_events = ((ev, fill_event(ev))[0] for ev in pv_events)
    pivoted_events = pivot_timeseries(pv_events, [pivot_key], static_keys)

    if dark_images:
        pivoted_events = correct_events(pivoted_events, pivot_key, dark_images)
    merged_events = zip_events(pivoted_events, ts_events)
    out_ev = reset_time(merged_events, timesource_key)
    yield from out_ev

def extract_darkfield(header, dark_key):
    cam_desc = [d for d in header['descriptors'] if dark_key in d['data_keys']][0]
    events = get_events_generator(cam_desc)
    events = list(((ev, fill_event(ev))[0] for ev in events))
    event = events[0]
    ims = (event['data'][dark_key] <<2) >>2
    return ims.mean(axis=0)
