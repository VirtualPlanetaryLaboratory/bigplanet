import subprocess
import numpy as np
import os
import pathlib
import warnings
import h5py
import multiprocessing as mp
import sys
import bigplanet as bp


def test_bpextract():
    # gets current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    # gets the number of cores on the machine
    cores = mp.cpu_count()
    if cores == 1:
        warnings.warn("There is only 1 core on the machine", stacklevel=3)
    else:
        # Run vspace
        if not (path / "BP_Extract").exists():
            subprocess.check_output(["vspace", "vspace.in"], cwd=path)

        # Run multi-planet
        if not (path / ".BP_Extract").exists():
            subprocess.check_output(["multiplanet", "vspace.in"], cwd=path)

        # Run bigplanet
        if not (path / ".BP_Extract_BPL").exists():
            subprocess.check_output(["bigplanet", "bpl.in", "-a"], cwd=path)

        file = bp.BPLFile(path / "BP_Extract.bpa")

        earth_Instellation_final = bp.ExtractColumn(
            file, 'earth:Instellation:final')
        sun_RotPer_initial = bp.ExtractColumn(file, 'sun:RotPer:initial')

        assert np.isclose(earth_Instellation_final[0], 1367.635318)
        assert np.isclose(earth_Instellation_final[1], 341.90883)

        assert np.isclose(sun_RotPer_initial[0], 86400.0)


if __name__ == "__main__":
    test_bpextract()
