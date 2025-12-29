import multiprocessing as mp
import os
import pathlib
import subprocess
import sys
import warnings
import shutil
import numpy as np
import bigplanet as bp


def test_ExtractArchive():
    # gets current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    # gets the number of cores on the machine
    cores = mp.cpu_count()
    if cores == 1:
        warnings.warn("There is only 1 core on the machine", stacklevel=3)
    else:
        # Remove anything from previous tests
        if (path / "BP_Extract").exists():
            shutil.rmtree(path / "BP_Extract")
        if (path / ".BP_Extract").exists():
            os.remove(path / ".BP_Extract")
        if (path / ".BP_Extract_BPL").exists():
            os.remove(path / ".BP_Extract_BPL")
        if (path / "BP_Extract.bpa").exists():
            os.remove(path / "BP_Extract.bpa")
        if (path / "BP_Extract.md5").exists():
            os.remove(path / "BP_Extract.md5")

        # Run vspace
        print("Running vspace.")
        sys.stdout.flush()
        subprocess.check_output(["vspace", "vspace.in"], cwd=path)

        # Run multi-planet
        print("Running MultiPlanet.")
        sys.stdout.flush()
        subprocess.check_output(["multiplanet", "vspace.in"], cwd=path)

        # Run bigplanet
        print("Running BigPlanet.")
        sys.stdout.flush()
        subprocess.check_output(["bigplanet", "bpl.in", "-a"], cwd=path)

        # MD5 checksumming is not functioning correctly as of v3.0
        file = bp.BPLFile(path / "BP_Extract.bpa", ignore_corrupt=True)

        earth_Instellation_final = bp.ExtractColumn(
            file, "earth:Instellation:final"
        )
        sun_RotPer_initial = bp.ExtractColumn(file, "sun:RotPer:initial")

        # VPlanet outputs Instellation in vplanet-internal units (M_sun * AU^2 / year^3)
        # Expected values: 1367.635318 W/m² → 1.937119e+33, 341.90883 W/m² → 4.842798e+32
        assert np.isclose(earth_Instellation_final[0], 1.937119e+33, rtol=1e-03)
        assert np.isclose(earth_Instellation_final[1], 4.842798e+32, rtol=1e-03)
        assert np.isclose(sun_RotPer_initial[0], 86400.0)

        shutil.rmtree(path / "BP_Extract")
        os.remove(path / ".BP_Extract")
        os.remove(path / ".BP_Extract_BPL")
        os.remove(path / "BP_Extract.bpa")
        os.remove(path / "BP_Extract.md5")

if __name__ == "__main__":
    test_ExtractArchive()
