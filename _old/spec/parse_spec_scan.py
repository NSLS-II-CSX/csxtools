from collections import OrderedDict
import re
from pprint import pprint
import pandas as pd

def parse_command(output):
    """Parse a spec command line

    Parameters
    -----------
    output : str
        The line of a spec command.
        Something like ``101.SIXC> ubr 1.6 0 0``

    Returns
    -------
    dct
        Dictionary of the spec command line
        e.g., {'cmd': 'ubr', 'diffractometer_type': 'SIXC', 'cmd_args': ['0.7', '0', '0'], 'cmd_idx': '80'}
    """
    if isinstance(output, list):
        if len(output) == 1:
            output = output[0]
    split = output.split()
    split[0] = split[0][:-1]
    dct = {}
    cmd_idx, diffrac_type = split[0].split('.')
    dct['cmd_idx'] = cmd_idx
    dct['diffractometer_type'] = diffrac_type
    dct['cmd'] = split[1]
    args = split[2:]
    if args:
        dct['cmd_args'] = args

    return dct


def spec_equals_to_dict(line):
    """Convert a spec output line to a dictionary

    Parameters
    ----------
    line : str
        A line that has a number of variables and their values separated
        by an equals sign.
        e.g., Two Theta = 88.854  Omega = -24.986  Lambda = 1.54

    Returns
    -------
    dict
        The spec output line converted into a dictionary
        e.g., {'Omega': -24.986, 'TwoTheta': 40.975, 'Lambda': 1.54}
    """
    # line = 'Two Theta = 88.854  Omega = -24.986  Lambda = 1.54'
    split = re.sub('[=]', '', line).split()
    # split = ['Two', 'Theta', '40.975', 'Omega', '24.986', 'Lambda', '1.54']
    dct = {}
    casted = []
    for s in split:
        try:
            s = float(s)
        except ValueError:
            pass
        casted.append(s)
    # casted = ['Two', 'Theta', 47.156, 'Omega', -24.986, 'Lambda', 1.54]

    # now the things i want are in the order N strings followed by one float
    # and I can convert that into a dictionary, woo!
    before = ''
    after = ''
    for val1, val2 in zip(casted, casted[1:]):
        if isinstance(val2, float):
            before += val1
            dct[before] = val2
            before = ''
        elif isinstance(val1, float):
            continue
        else:
            before += val1
    # dct = {'Omega': -24.986, 'TwoTheta': 40.975, 'Lambda': 1.54}
    return dct


def parse_br(output):
    """See ``parse_ubr``"""
    return parse_ubr(output)


def parse_ubr(output):
    """Parse the output of the ``ubr`` or ``br`` spec command

    Parameters
    ----------
    output : list
        List of lines from the spec output including the line with the
        ``ubr`` or ``br`` command
        e.g.,
        101.SIXC> ubr 1.6 0 0

    Returns
    -------
    meta : dict
        Spec ``ubr`` command converted into a dictionary
        e.g.,
        {'H': 0.7, 'K': 0.0, 'L': 0.0,
         'cmd': 'ubr',
         'cmd_idx': '80',
         'diffractometer_type': 'SIXC'}
    """
    # parse the spec command
    meta = parse_command(output[0])
    cmd_args = meta.pop('cmd_args')
    meta['H'] = float(cmd_args[0])
    meta['K'] = float(cmd_args[1])
    meta['L'] = float(cmd_args[2])

    return meta


def parse_wh(output):
    """Parse the output of the ``wh`` spec command

    Parameters
    ----------
    output : list
        List of lines from the spec output including the line with the ``wh`` command
        e.g.:

            100.SIXC> wh

            H K L =  1.5  -1.0472e-05  0
            Alpha = 0  Beta = 0  Azimuth = -90
            Two Theta = 97.181  Omega = -24.986  Lambda = 1.54

                Delta     Theta       Chi       Phi        Mu     Gamma
              97.1808   23.6040    0.0000   24.9860    0.0000    0.0000

    Returns
    -------
    meta : dict
        The dictionary of all non-motor information
    motors : dict
        The dictionary of motor information
    """
    # parse the spec command
    meta = parse_command(output[0])
    # add the alpha beta azimuth line to the meta dict
    meta.update(spec_equals_to_dict(output[2]))
    # add the two theta, omega, lambda line to the meta dict
    meta.update(spec_equals_to_dict(output[3]))
    # add hkl to the meta dict
    hkl = output[1].split()
    meta.update({miller: pos for miller, pos in zip(hkl[:3], hkl[-3:])})
    # format the dictionary of motors
    meta['motors'] = {name: pos for name, pos in zip(output[4].split(), output[5].split())}
    return meta


motor_mapping = {'del': 'Delta',
                 'th': 'Theta',
                 'chi': 'Chi',
                 'phi': 'Phi',
                 'mu': 'Mu',
                 'gam': 'Gamma'}


def parse_reflection(refl_lines):
    """Parse one of the reflections from the output of ``pa``

    Parameters
    ----------
    refl_lines : list
        List of the three lines that correspond to a reflection from the
        output of the spec command ``pa``
        e.g.,
        Primary Reflection (at lambda 1.54):
         del th chi phi mu gam = 60 30 0 0 0 0
                       H K L = 1 0 0

    Returns
    -------
    refl : dict
        Dictionary of reflection information
        e.g.,
        {'Mu': '0', 'Phi': '0', 'H': '1', 'Chi': '0', 'Theta': '30',
         'wavelength': '1.54', 'K': '0', 'Delta': '60', 'L': '0', 'Gamma': '0'}
    """
    mtr_line = refl_lines[1].split()
    hkl = refl_lines[2].split()
    wavelength = re.sub('[():]', '', refl_lines[0]).split()[-1]
    motors = {motor_mapping[mtr]: pos for mtr, pos in zip(mtr_line[:6], mtr_line[-6:])}
    hkl = {miller: pos for miller, pos in zip(hkl[:3], hkl[-3:])}
    refl = {'wavelength': wavelength}
    refl.update(motors)
    refl.update(hkl)
    return refl


def parse_lattice(lattice_lines):
    """Parse the lattice lines from the output of ``pa``

    Parameters
    ----------
    lattice_lines : list
        The three lattice lines from the spec command ``pa``
        that are related to the Lattice
        e.g.,
          Lattice Constants (lengths / angles):
                      real space = 1.54 1.54 1.54 / 90 90 90
                reciprocal space = 4.08 4.08 4.08 / 90 90 90

    Returns
    -------
    lattice : dict
        Dictionary of lattice info (a, b, c, alpha, beta, gamma) separated
        into 'real' and 'recip' keys
        e.g.,
        {'real': {'a': '1.54', 'c': '1.54', 'b': '1.54',
                  'beta': '90', 'alpha': '90', 'gamma': '90'},
         'recip': {'c*': '4.08', 'a*': '4.08', 'beta*': '90',
                   'b*': '4.08', 'alpha*': '90', 'gamma*': '90'}}
    """
    # get rid of the '=' and '/' characters
    real_values = re.sub('[=/]', '', lattice_lines[1]).split()[-6:]
    recip_values = re.sub('[=/]', '', lattice_lines[2]).split()[-6:]
    # format the keys
    real_labels = ['a', 'b', 'c', 'alpha', 'beta', 'gamma']
    recip_labels = [r + '*' for r in real_labels]
    lattice = {}
    lattice['real'] = {r: val for r, val in zip(real_labels, real_values)}
    lattice['recip'] = {r: val for r, val in zip(recip_labels, recip_values)}
    return lattice


def parse_azimuthal(azimuthal_lines):
    """Parse the azimuthal bit from the spec ``pa`` command

    Parameters
    ----------
    azimuthal_lines : list
        List of lines from the spec ``pa`` command that correspond
        to the ``Azimuthal Reference`` bit
        e.g.,

        Azimuthal Reference:
                           H K L = 0 0 1
                       sigma tau = 0 0

                Gamma-arm length = 585 mm
                  Gamma tracking = Off
    Returns
    -------
    dict
        Dictionary of azimuthal information
        e.g.,
        {'tau': '0', 'gamma tracking': 'Off', 'H': '0', 'K': '0', 'L': '1',
         'gamma arm length': '585 mm', 'sigma': '0'}}
    """
    # give the four relevant lines useful names
    hkl = azimuthal_lines[1].split()
    sigma_tau = azimuthal_lines[2].split()
    gamma_length = azimuthal_lines[3].split()
    gamma_tracking = azimuthal_lines[4].split()
    # put the information into a dictionary
    dct = {miller: value for miller, value in zip(hkl[:3], hkl[-3:])}
    dct.update({k: v for k, v in zip(sigma_tau[:2], sigma_tau[-2:])})
    dct['gamma arm length'] = ' '.join(gamma_length[-2:])
    dct['gamma tracking'] = gamma_tracking[-1]
    # and, uh, return it...
    return dct


def parse_mono(mono_lines):
    """Parse the Monochromator lines from the spec command ``pa``

    Parameters
    ----------
    mono_lines : list
        The three lines that correspond to the monochromator.
        e.g.,
          Monochromator:
                   d-spacing = 0 Angstoms
                          Lambda = 1.54
    Returns
    -------
    dct
        A dictionary containing two keys: ['d_spacing', 'wavelength']
        Note:
         - wavelength is a float in units of angstroms
         - d_spacing is a string with the units embedded in the string
           as I am unsure if this value is ALWAYS reported in angstroms or not
        e.g.,
        {'wavelength': 1.54, 'd_spacing': '0 Angstoms'}
    """
    dct = {'d_spacing': ' '.join(mono_lines[1].split()[-2:]),
           'wavelength': float(mono_lines[2].split()[-1])}
    return dct


def parse_cutpoints(cutpoints_lines):
    motors = cutpoints_lines[1].split()
    positions = cutpoints_lines[2].split()
    motors = {motor_mapping[mtr]: pos for mtr, pos in zip(motors[:6], positions[-6:])}
    return motors


def parse_pa(output):
    """Parse the output from the spec command ``pa``

    Parameters
    ----------
    output : list
        List of lines from the spec command ``pa``
        e.g.,
        107.SIXC> pa

        Six-Circle Geometry, Omega fixed (four circle, Mu = Gamma = 0) (mode 0)
        Sector 0

          Primary Reflection (at lambda 1.54):
           del th chi phi mu gam = 60 30 0 0 0 0
                           H K L = 1 0 0

          Secondary Reflection (at lambda 1.54):
           del th chi phi mu gam = 60 30 0 90 0 0
                           H K L = 0 1 0

          Lattice Constants (lengths / angles):
                      real space = 1.54 1.54 1.54 / 90 90 90
                reciprocal space = 4.08 4.08 4.08 / 90 90 90

          Azimuthal Reference:
                           H K L = 0 0 1
                       sigma tau = 0 0

                Gamma-arm length = 585 mm
                  Gamma tracking = Off

          Monochromator:
                   d-spacing = 0 Angstoms
                          Lambda = 1.54

          Cut Points:
              del   th  chi  phi   mu  gam
             -180 -180 -180 -180 -180 -180

    Returns
    -------
    dict
        Dictionary of the ``pa`` output
        e.g.,
        {'azimuthal': {'H': '0',
           'K': '0',
           'L': '1',
           'gamma arm length': '585 mm',
           'gamma tracking': 'Off',
           'sigma': '0',
           'tau': '0'},
          'cmd': 'pa',
          'cmd_idx': '107',
          'cut_points': {'Chi': '-180',
           'Delta': '-180',
           'Gamma': '-180',
           'Mu': '-180',
           'Phi': '-180',
           'Theta': '-180'},
          'description': 'Six-Circle Geometry, Omega fixed (four circle, Mu = Gamma = 0) (mode 0)',
          'diffractometer_type': 'SIXC',
          'lattice': {'real': {'a': '1.54',
            'alpha': '90',
            'b': '1.54',
            'beta': '90',
            'c': '1.54',
            'gamma': '90'},
           'recip': {'a*': '4.08',
            'alpha*': '90',
            'b*': '4.08',
            'beta*': '90',
            'c*': '4.08',
            'gamma*': '90'}},
          'mono': {'d_spacing': '0 Angstoms', 'wavelength': 1.54},
          'refl0': {'Chi': '0',
           'Delta': '60',
           'Gamma': '0',
           'H': '1',
           'K': '0',
           'L': '0',
           'Mu': '0',
           'Phi': '0',
           'Theta': '30',
           'wavelength': '1.54'},
          'refl1': {'Chi': '0',
           'Delta': '60',
           'Gamma': '0',
           'H': '0',
           'K': '1',
           'L': '0',
           'Mu': '0',
           'Phi': '90',
           'Theta': '30',
           'wavelength': '1.54'},
          'sector': '0'}
    """
    meta = parse_command(output[0])
    # add the description to the spec command
    meta['description'] = output[1]
    meta['sector'] = output[2].split()[1]
    # add the primary reflection
    meta['refl0'] = parse_reflection(output[3:6])
    meta['refl1'] = parse_reflection(output[6:9])
    meta['lattice'] = parse_lattice(output[9:12])
    meta['azimuthal'] = parse_azimuthal(output[12:17])
    meta['mono'] = parse_mono(output[17:20])
    meta['cut_points'] = parse_cutpoints(output[20:23])

    return meta


def get_commands(filename):
    with open(filename, 'r') as f:
        commands = []
        lines = []
        try:
            while True:
                line = f.next().strip()
                if 'SIXC' in line:
                    if lines:
                        commands.append([command, lines])
                    lines = []
                    command = line.split()[1]
                elif line == '\n' or line == '' or 'state is stored' in line:
                    # skip empty lines
                    continue

                lines.append(line)
        except StopIteration:
            commands.append([command, lines])
            pass
    return commands


def parse_spec_output(spec_output_file):
    spec_commands = get_commands(spec_output_file)
    spec_mapping = {'ubr': parse_ubr,
                    'br': parse_br,
                    'wh': parse_wh,
                    'pa': parse_pa}
    parsed = [spec_mapping.get(command, None)(output)
              for command, output in spec_commands]
    return parsed


def parsed_to_dataframe(parsed):
    # ubr and wh can be zipped together to produce
    # pairs of desired position/actual position
    ubr = [dct for dct in parsed if dct['cmd'] == 'ubr']
    wh = [dct for dct in parsed if dct['cmd'] == 'wh']
    meta = [dct for dct in parsed if dct['cmd'] not in ['ubr', 'wh']]
    mapping = {'H (target)': ('desired', 'H'),
               'K (target)': ('desired', 'K'),
               'L (target)': ('desired', 'L'),
               'H (actual)': ('actual', 'H'),
               'K (actual)': ('actual', 'K'),
               'L (actual)': ('actual', 'L'),
               'Delta': ('actual', ['motors', 'Delta']),
               'Theta': ('actual', ['motors', 'Theta']),
               'Chi': ('actual', ['motors', 'Chi']),
               'Phi': ('actual', ['motors', 'Phi']),
               'Mu': ('actual', ['motors', 'Mu']),
               'Gamma': ('actual', ['motors', 'Gamma']),
    }
    data = {key: [] for key in mapping.keys()}
    index = []
    for desired, actual in zip(ubr, wh):
        index.append('%s-%s' % (desired['cmd_idx'], actual['cmd_idx']))
        for k, v in mapping.items():
            val = locals()[v[0]]
            v = v[1]
            if not isinstance(v, list):
                v = [v]
            for item in v:
                val = val[item]
            data[k].append(val)


    series = {k: pd.Series(v, index) for k, v in data.items()}
    df = pd.DataFrame(series)
    return df, meta


if __name__ == "__main__":
    parsed = parse_spec_output('spec-h-scan.txt')
    df, meta = parsed_to_dataframe(parsed)
    print(df)
    print("\nMETADATA"
          "\n--------")
    pprint(meta)


