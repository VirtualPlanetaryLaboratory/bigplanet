import multiprocessing as mp
import os
import pathlib
import subprocess
import sys
import warnings
import shutil
import numpy as np
import bigplanet as bp

def test_UlyssesForward():
    # gets current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    # gets the number of cores on the machine
    cores = mp.cpu_count()
    if cores == 1:
        warnings.warn("There is only 1 core on the machine", stacklevel=3)
    else:
        # If present, remove files from previous run
        if (path / "BP_Extract").exists():
            shutil.rmtree(path / "BP_Extract")
        if (path / ".BP_Extract").exists():
            os.remove(path / ".BP_Extract")
        if (path / "User.csv").exists():
            os.remove(path / "User.csv")

        # Run vspace
        print("Running vspace")
        sys.stdout.flush()
        subprocess.check_output(["vspace", "vspace.in"], cwd=path)

        # Run multi-planet
        print("Running multiplanet")
        sys.stdout.flush()
        # subprocess.check_output(["multiplanet", "vspace.in"], cwd=path)

        # # Run bigplanet
        # print("Running bigplanet")
        # sys.stdout.flush()
        # subprocess.check_output(["bigplanet", "bpl.in"], cwd=path)

        # file = path / "User.csv"

        # data = bp.CSVToDict(file, 1)

        # value = float(data["earth:TCore:forward"][451])

        # assert np.isclose(value, 4999.131849)

        # shutil.rmtree(path / "BP_Extract")
        # os.remove(path / ".BP_Extract")
        # os.remove(path / "User.csv")

if __name__ == "__main__":
    test_UlyssesForward()
