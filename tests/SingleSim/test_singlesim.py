import multiprocessing as mp
import os
import pathlib
import subprocess
import sys
import warnings
import shutil
import numpy as np
import bigplanet as bp

def test_SingleSim():
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
        if (path / "Test.bpf").exists():
            os.remove(path / "Test.bpf")

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

        # file = bp.BPLFile(path / "Test.bpf")

        # earth_Tman_forward = bp.ExtractColumn(file, "earth:TMan:forward")
        # earth_Tcore_inital = bp.ExtractColumn(file, "earth:TCore:initial")

        # assert np.isclose(earth_Tman_forward[0][-1], 2257.850930)
        # assert np.isclose(earth_Tcore_inital[0], 6000.00000)


        # shutil.rmtree(path / "BP_Extract")
        # os.remove(path / ".BP_Extract")
        # os.remove(path / "Test.bpf")

if __name__ == "__main__":
    test_SingleSim()
