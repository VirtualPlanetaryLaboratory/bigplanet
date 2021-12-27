import subprocess
import numpy as np
import os
import pathlib
import warnings
import h5py
import multiprocessing as mp
import sys
import bigplanet as bp


def test_singlesim():
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
        if not (path / "Test.bpf").exists():
            subprocess.check_output(["bigplanet", "bpl.in"], cwd=path)

        file = bp.BPLFile(path / "Test.bpf")

        earth_Tman_forward = bp.ExtractColumn(file, 'earth:TMan:forward')
        earth_Tcore_inital = bp.ExtractColumn(file, 'earth:TCore:initial')

        assert np.isclose(earth_Tman_forward[0][-1], 2257.850930)
        assert np.isclose(earth_Tcore_inital[0], 6000.00000)


if __name__ == "__main__":
    test_singlesim()
