import numpy as np
from databroker import get_table
import .settings as settings

def table_to_sixc(table, angles=None):
    if angles is None:
        angles = settings.diff_angles

    # First lets get the
