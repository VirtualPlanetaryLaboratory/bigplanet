import subprocess as sub
import numpy as np
import os
cwd = os.path.dirname(os.path.realpath(__file__))
import warnings
import h5py
import multiprocessing as mp
import sys
import bigplanet as bp

def test_bpstats():
    #gets the number of cores on the machine
    cores = mp.cpu_count()
    if cores == 1:
        warnings.warn("There is only 1 core on the machine",stacklevel=3)
    else:
        #removes checkpoint files
        cp = cwd+'/.BP_Stats'
        sub.run(['rm', cp],cwd=cwd)
        cp_hdf5 = cwd+'/.BP_Stats_BPL'
        sub.run(['rm', cp_hdf5],cwd=cwd)
        #removes the folders from when vspace is ran
        dir = cwd+'/BP_Stats'
        sub.run(['rm', '-rf', dir],cwd=cwd)
        sub.run(['rm', '-rf', (dir + '.bpl')],cwd=cwd)
        #runs vspace
        sub.run(['vspace','vspace.in'],cwd=cwd)
        #runs multi-planet
        sub.run(['multi-planet','vspace.in'],cwd=cwd)
        #runs bigplanet
        sub.run(['bigplanet','vspace.in'],cwd=cwd)

        #reads in the hdf5 file
        file = h5py.File((dir + '.bpl'),'r')

        earth_TMan_min = bp.ExtractColumn(file,'earth_TMan_min')
        earth_235UNumMan_max = bp.ExtractColumn(file,'earth_235UNumMan_max')
        earth_TCMB_mean = bp.ExtractColumn(file,'earth_TCMB_mean')
        earth_FMeltUMan_geomean = bp.ExtractColumn(file,'earth_FMeltUMan_geomean')
        earth_BLUMan_stddev = bp.ExtractColumn(file,'earth_BLUMan_stddev')

        assert np.isclose(earth_TMan_min[0],2257.85093)
        assert np.isclose(earth_235UNumMan_max[0],2.700598e+28)
        assert np.isclose(earth_TCMB_mean[0],4359.67230935255)
        assert np.isclose(earth_FMeltUMan_geomean[0],0.20819565439935903)
        assert np.isclose(earth_BLUMan_stddev[0],18.265090016213463)


if __name__ == "__main__":
    test_bpstats()
