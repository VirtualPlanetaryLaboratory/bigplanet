import subprocess
import numpy as np
import os
import pathlib
import multiprocessing as mp
import warnings
import sys


def test_bpstatus():
    # gets current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    # gets the number of cores on the machine
    cores = mp.cpu_count()
    if cores == 1:
        warnings.warn("There is only 1 core on the machine", stacklevel=3)
    else:
        # Run vspace
        if not (path / "BP_Status").exists():
            subprocess.check_output(["vspace", "vspace.in"], cwd=path)

        # Run multi-planet
        if not (path / ".BP_Status").exists():
            subprocess.check_output(["multiplanet", "vspace.in"], cwd=path)

        # Run bigplanet
        if not (path / ".BP_Status_BPL").exists():
            subprocess.check_output(["bigplanet", "bpl.in", "-a"], cwd=path)
            subprocess.check_output(["bpstatus", "vspace.in"], cwd=path)

        file = (path / "BP_Status.bpa")

        # checks if the bpl files exist
        assert os.path.isfile(file) == True


if __name__ == "__main__":
    test_bpstatus()
