import multiprocessing as mp
import os
import pathlib
import subprocess
import sys
import warnings
import shutil
import h5py
import numpy as np

import bigplanet as bp


def test_ExtractFilterRaw():
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

        # Run multiplanet
        print("Running multiplanet")
        # sys.stdout.flush()
        # subprocess.check_output(["multiplanet", "vspace.in"], cwd=path)

        # Run BigPlanet
        print("Running bigplanet")
        sys.stdout.flush()
        # subprocess.check_output(["bigplanet", "bpl.in"], cwd=path)

        # file = bp.BPLFile(path / "Test.bpf")

        # earth_Instellation_final = bp.ExtractColumn(
        #     file, "earth:Instellation:final"
        # )
        # sun_Luminosity_option = bp.ExtractColumn(
        #     file, "sun:dLuminosity:option"
        # )
        # earth_Mass_option = bp.ExtractColumn(file, "earth:dMass:option")
        # vpl_stoptime_option = bp.ExtractColumn(file, "vpl:dStopTime:option")
        # earth_tman_forward = bp.ExtractColumn(file, "earth:TMan:forward")

        # print(earth_Instellation_final[1])
        # assert np.isclose(earth_Instellation_final[1], 341.90883)
        # assert np.isclose(sun_Luminosity_option[0], 3.846e26)
        # assert np.isclose(earth_Mass_option[1], -1.5)
        # assert np.isclose(vpl_stoptime_option[0], 4.5e9)
        # assert np.isclose(earth_tman_forward[0][0], 3000.0)

        # shutil.rmtree(path / "BP_Extract")
        # os.remove(path / ".BP_Extract")
        # os.remove(path / "Test.bpf")


if __name__ == "__main__":
    test_ExtractFilterRaw()
