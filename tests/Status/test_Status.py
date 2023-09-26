import multiprocessing as mp
import os
import pathlib
import subprocess
import sys
import warnings
import shutil
import numpy as np


def test_bpstatus():
    # gets current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    # gets the number of cores on the machine
    cores = mp.cpu_count()
    if cores == 1:
        warnings.warn("There is only 1 core on the machine", stacklevel=3)
    else:
        if (path / "BP_Status").exists():
            shutil.rmtree(path / "BP_Status")
        if (path / ".BP_Status").exists():
            os.remove(path / ".BP_Status")
        if (path / ".BP_Status_BPL").exists():
            os.remove(path / ".BP_Status_BPL")
        if (path / "BP_Status.bpa").exists():
            os.remove(path / "BP_Status.bpa")
        if (path / "../BP_Status.md5").exists():
            os.remove(path / "../BP_Status.md5")
        if (path / "BP_Status.md5").exists():
            os.remove(path / "BP_Status.md5")

        # Run vspace
        subprocess.check_output(["vspace", "vspace.in"], cwd=path)

        # Run multi-planet
#         subprocess.check_output(["multiplanet", "vspace.in"], cwd=path)

#         # Run bigplanet
# #        subprocess.check_output(["bigplanet", "-ignorecorrupt", "bpl.in", "-a"], cwd=path)
#         subprocess.check_output(["bigplanet", "bpl.in", "-a"], cwd=path)
#         subprocess.check_output(["bpstatus", "vspace.in"], cwd=path)

#         file = path / "BP_Status.bpa"

#         # checks if the bpl files exist
#         assert os.path.isfile(file) == True

#         shutil.rmtree(path / "BP_Status")
#         os.remove(path / ".BP_Status")
#         os.remove(path / ".BP_Status_BPL")
#         os.remove(path / "BP_Status.bpa")
#         os.remove(path / "BP_Status.md5")

if __name__ == "__main__":
    test_bpstatus()
