import subprocess
import numpy as np
import os
import warnings
import h5py
import multiprocessing as mp
import sys
import pathlib
import bigplanet as bp


def test_bpstats():
    # gets current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    # gets the number of cores on the machine
    cores = mp.cpu_count()
    if cores == 1:
        warnings.warn("There is only 1 core on the machine", stacklevel=3)
    else:
        # Run vspace
        if not (path / "BP_Stats").exists():
            subprocess.check_output(["vspace", "vspace.in"], cwd=path)

        # Run multi-planet
        if not (path / ".BP_Stats").exists():
            subprocess.check_output(["multiplanet", "vspace.in"], cwd=path)

        # Run bigplanet
        if not (path / "BP_Stats.bpa").exists():
            subprocess.check_output(["bigplanet", "bpl.in", "-a"], cwd=path)

        file = bp.BPLFile(path / "BP_Stats.bpa")

        earth_TMan_min = bp.ExtractColumn(file, 'earth:TMan:min')
        earth_235UNumMan_max = bp.ExtractColumn(file, 'earth:235UNumMan:max')
        earth_TCMB_mean = bp.ExtractColumn(file, 'earth:TCMB:mean')
        earth_FMeltUMan_geomean = bp.ExtractColumn(file, 'earth:FMeltUMan:geomean')
        earth_BLUMan_stddev = bp.ExtractColumn(file, 'earth:BLUMan:stddev')

        assert np.isclose(earth_TMan_min[0], 2257.85093)
        assert np.isclose(earth_235UNumMan_max[0], 2.700598e+28)
        assert np.isclose(earth_TCMB_mean[0], 4359.67230935255)
        assert np.isclose(earth_FMeltUMan_geomean[0], 0.20819565439935903)
        assert np.isclose(earth_BLUMan_stddev[0], 18.285373298439122)


if __name__ == "__main__":
    test_bpstats()
