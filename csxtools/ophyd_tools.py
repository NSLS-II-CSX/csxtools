from ophyd.userapi.scan_api import Scan, AScan, DScan, Count, estimate
from prettytable import PrettyTable
from collections import OrderedDict


class CSXAScan(AScan):
    def __call__(self, *args, **kwargs):
        super(CSXAScan, self).__call__(*args, **kwargs)

    def post_scan(self):
        super(CSXAScan, self).post_scan()
        x = getattr(self.data[-1], self.positioners[0].name)
        positioners = [pos.name for pos in self.positioners]
        detectors = sorted([det for det in self.data[-1].data_dict.keys()
                            if not det in positioners])
        estimates = {}
        for pos in positioners:
            estimates[pos] = {}
            x = getattr(self.data[-1], pos)
            for det in detectors:
                y = getattr(self.data[-1], det)
                estimates[pos][det] = estimate(x, y)
        estimate_keys = set()
        for pos, det_dict in estimates.items():
            for det, est in det_dict.items():
                for est_key in est.items():
                    estimate_keys.add(est_key)
        print_estimate_table_det_rows(estimates)


def print_estimate_table_det_rows(estimate_dict):
    """Pretty print the estimates to the console

    It will look like this:

    Estimates for x axis: theta
    +----------+-------------+-----------------------------+
    | x=theta  |    avg_y    |             cen             |
    +----------+-------------+-----------------------------+
    |sclr_chan1|  50000005.0 |                             |
    |sclr_chan2|5051.33333333|                             |
    |sclr_chan3|    4564.5   |        -6.59804608824       |
    |sclr_chan4|    2710.0   |                             |
    |sclr_chan5|    4950.5   |(-6.3003138319200005, 4950.5)|
    |sclr_chan6|     0.0     |                             |
    |sclr_chan7|     0.0     |                             |
    |sclr_chan8|     0.0     |                             |
    |sclr_time |  1.0000001  |                             |
    +----------+-------------+-----------------------------+
    """
    estimate_keys = set()
    for pos, det_dict in estimate_dict.items():
        for det, est in det_dict.items():
            print('est: {}'.format(est))
            for k, v in est.items():
                estimate_keys.add(k)
    estimate_keys = list(estimate_keys)
    estimate_keys = sorted(estimate_keys, key=lambda s: s.lower())
    for pos, det_dict in estimate_dict.items():
        table = PrettyTable(['x={}'.format(pos)] + estimate_keys)
        table.align['Detector'] = 'l'
        table.padding_width = 0
        # sort the detectors
        det_names = sorted(det_dict.keys(), key=lambda s: s.lower())
        # iterate over the sorted detectors
        for det in det_names:
            # grab the estimate info
            est_dict = det_dict[det]
            row = [det]
            # format the rows
            for key in estimate_keys:
                row.append(est_dict.get(key, ''))
            table.add_row(row)
        print("Estimates for x axis: {}".format(pos))
        print(table)


def print_estimate_table_det_cols(estimate_dict):
    """Pretty print the estimates to the console

    It will look like this:

    Estimates for x axis: theta
    +--------------+--------------+--------------+
    |   x=theta    |  sclr_chan1  |  sclr_chan2  |
    +--------------+--------------+--------------+
    |    avg_y     |  50000005.0  |5052.33333333 |
    |     cen      |              |-6.19782822048|
    |center_of_mass|-6.49865454515|-6.49862825925|
    |  fwhm_left   |              |              |
    |  fwhm_right  |              |              |
    |    width     |              |              |
    |  x_at_ymax   |-6.00265021968|-6.00265021968|
    |  x_at_ymin   |-6.00265021968|-6.39784944248|
    |     ymax     |  50000005.0  |    5053.0    |
    |     ymin     |  50000005.0  |    5052.0    |
    +--------------+--------------+--------------+

    Parameters
    ----------
    estimate_dict : dict
        nested dictionary = {
            "pos1" : {
                "det1" : {
                    stat1 : val,
                    stat2 : val,
                    ... },
                "det2" : {
                    ...
                },
            "pos2" : { ... },
        }
    """
    estimate_keys = set()
    for pos, det_dict in estimate_dict.items():
        for det, est in det_dict.items():
            for k, v in est.items():
                estimate_keys.add(k)
    estimate_keys = list(estimate_keys)
    estimate_keys = sorted(estimate_keys, key=lambda s: s.lower())
    for pos, det_dict in estimate_dict.items():
        det_names = sorted(det_dict.keys(), key=lambda s: s.lower())
        table = PrettyTable(['x={}'.format(pos)] + det_names)
        table.align['Estimate Keys'] = 'l'
        table.padding_width = 0
        # sort the detectors
        # iterate over the sorted detectors
        rows_dict = OrderedDict()
        for det in det_names:
            # grab the estimate info
            est_dict = det_dict[det]
            for estimate_key in estimate_keys:
                try:
                    rows_dict[estimate_key]
                except KeyError:
                    rows_dict[estimate_key] = [estimate_key]
                rows_dict[estimate_key].append(est_dict.get(estimate_key, ''))
        for row in rows_dict.values():
            table.add_row(row)
        print("Estimates for x axis: {}".format(pos))
        print(table)



