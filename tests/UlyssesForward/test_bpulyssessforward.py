import subprocess
import numpy as np
import os
import pathlib
import warnings
import h5py
import multiprocessing as mp
import sys
import bigplanet as bp


def test_ulyssesforward():
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
        if not (path / "User.csv").exists():
            subprocess.check_output(["bigplanet", "bpl.in"], cwd=path)

        file = path / "User.csv"

        data = bp.CSVToDict(file, 1)

        value = float(data['earth:TCore:forward'][451])

        assert np.isclose(
            value, 4999.131849)


if __name__ == "__main__":
    test_ulyssesforward()
