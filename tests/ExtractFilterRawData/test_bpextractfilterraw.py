import subprocess
import numpy as np
import os
import pathlib
import warnings
import h5py
import multiprocessing as mp
import sys
import bigplanet as bp

def test_bpextract():
    #gets current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    #gets the number of cores on the machine
    cores = mp.cpu_count()
    if cores == 1:
        warnings.warn("There is only 1 core on the machine",stacklevel=3)
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

        file  = bp.BPLFile(path / "Test.bpf")

        earth_Instellation_final = bp.ExtractColumn(file,'earth:Instellation:final')
        sun_Luminosity_option = bp.ExtractColumn(file,'sun:dLuminosity:option')
        earth_Mass_option = bp.ExtractColumn(file,'earth:dMass:option')
        vpl_stoptime_option = bp.ExtractColumn(file,'vpl:dStopTime:option')
        earth_tman_forward = bp.ExtractColumn(file,'earth:TMan:forward')




        assert np.isclose(earth_Instellation_final[1],341.90883)
        assert np.isclose(sun_Luminosity_option[0],3.846e26)
        assert np.isclose(earth_Mass_option[1],-1.5)
        assert np.isclose(vpl_stoptime_option[0],4.5e9)
        assert np.isclose(earth_tman_forward[0][0],3000.0)





if __name__ == "__main__":
    test_bpextract()
