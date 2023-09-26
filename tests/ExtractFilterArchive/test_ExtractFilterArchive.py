import multiprocessing as mp
import os
import pathlib
import subprocess
import sys
import warnings
import shutil
import numpy as np
import bigplanet as bp


def test_ExtractFilterArchive():
    # gets current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    # gets the number of cores on the machine
    cores = mp.cpu_count()
    if cores == 1:
        warnings.warn("There is only 1 core on the machine", stacklevel=3)
    else:
        # Remove any old test files/dirs
        if (path / "BP_Extract").exists():
            shutil.rmtree(path / "BP_Extract")
        if (path / ".BP_Extract").exists():
            os.remove(path / ".BP_Extract")
        if (path / ".BP_Extract_BPL").exists():
            os.remove(path / ".BP_Extract_BPL")   
        if (path / "BP_Extract.bpa").exists():
            os.remove(path / "BP_Extract.bpa")
        if (path / "Test.bpf").exists():
            os.remove(path / "Test.bpf")
        if (path / "BP_Extract.md5").exists():
            os.remove(path / "BP_Extract.md5")

        # Run vspace
        print("Running vspace.")
        sys.stdout.flush()
        subprocess.check_output(["vspace", "vspace.in"], cwd=path)

        # Run multi-planet
        print("Running MultiPlanet.")
        # sys.stdout.flush()
        # subprocess.check_output(["multiplanet", "vspace.in"], cwd=path)

        # Run bigplanet
        print("Creating BigPlanet archive.")
        sys.stdout.flush()
        # subprocess.check_output(["bigplanet", "bpl.in", "-a"], cwd=path)

        # # Run bigplanet
        # print("Creating BigPlanet file.")
        # sys.stdout.flush()
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

        # assert np.isclose(earth_Instellation_final[1], 341.90883)
        # assert np.isclose(sun_Luminosity_option[0], 3.846e26)
        # assert np.isclose(earth_Mass_option[1], -1.5)
        # assert np.isclose(vpl_stoptime_option[0], 4.5e9)
        # assert np.isclose(earth_tman_forward[0][0], 3000.0)

        # shutil.rmtree(path / "BP_Extract")
        # os.remove(path / ".BP_Extract")
        # os.remove(path / ".BP_Extract_BPL")
        # os.remove(path / "BP_Extract.bpa")
        # os.remove(path / "Test.bpf")
        # os.remove(path / "BP_Extract.md5")

if __name__ == "__main__":
    test_ExtractFilterArchive()
