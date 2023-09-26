import multiprocessing as mp
import os
import pathlib
import subprocess
import sys
import warnings
import shutil

import numpy as np


def test_CreateHDF5():
    # gets current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    # gets the number of cores on the machine
    cores = mp.cpu_count()
    if cores == 1:
        warnings.warn("There is only 1 core on the machine", stacklevel=3)
    else:
        # Remove anything from previous tests
        if (path / "BP_CreateHDF5").exists():
            shutil.rmtree(path / "BP_CreateHDF5")
        if (path / ".BP_CreateHDF5").exists():
            os.remove(path / ".BP_CreateHDF5")
        if (path / ".BP_CreateHDF5_BPL").exists():
            os.remove(path / ".BP_CreateHDF5_BPL")
        if (path / "BP_CreateHDF5.bpa").exists():
            os.remove(path / "BP_CreateHDF5.bpa")
        if (path / "BP_CreateHDF5.md5").exists():
            os.remove(path / "BP_CreateHDF5.md5")

        # Run vspace
        print("Running vspace.")
        sys.stdout.flush()
        subprocess.check_output(["vspace", "vspace.in"], cwd=path)

        # Run multi-planet
        print("Running MultiPlanet.")
        # sys.stdout.flush()
        # subprocess.check_output(["multiplanet", "vspace.in"], cwd=path)

        # Run bigplanet
        # print("Running BigPlanet.")
        # sys.stdout.flush()
        # subprocess.check_output(["bigplanet", "bpl.in", "-a"], cwd=path)

        # file = path / "BP_CreateHDF5.bpa"

        # # checks if the bpl files exist
        # assert os.path.isfile(file) == True

        # shutil.rmtree(path / "BP_CreateHDF5")
        # os.remove(path / ".BP_CreateHDF5")
        # os.remove(path / ".BP_CreateHDF5_BPL")
        # os.remove(path / "BP_CreateHDF5.bpa")
        # os.remove(path / "BP_CreateHDF5.md5")

if __name__ == "__main__":
    test_CreateHDF5()
