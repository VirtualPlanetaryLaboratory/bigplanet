import hashlib
import multiprocessing as mp
import os
import pathlib
import subprocess
import sys
import warnings

import h5py
import numpy as np

import bigplanet as bp


def test_bpextract():
    # gets current path
    path = pathlib.Path(__file__).parents[0].absolute()
    sys.path.insert(1, str(path.parents[0]))

    # gets the number of cores on the machine
    cores = mp.cpu_count()
    if cores == 1:
        warnings.warn("There is only 1 core on the machine", stacklevel=3)
    else:
        # Run vspace
        if not (path / "BP_Extract").exists():
            subprocess.check_output(["vspace", "vspace.in"], cwd=path)

        # Run multi-planet
        if not (path / ".BP_Extract").exists():
            subprocess.check_output(["multiplanet", "vspace.in"], cwd=path)

        # Run bigplanet
        if not (path / ".BP_Extract_BPL").exists():
            subprocess.check_output(["bigplanet", "bpl.in", "-a"], cwd=path)

        bpa = path / "BP_Extract.bpa"

        md5file = path / "BP_Extract.md5"
        with open(md5file, "r") as md5:
            array = md5.read().splitlines()
            md5_old = array[0]
            with open(bpa, "rb") as f:
                file_hash = hashlib.md5()
                for chunk in iter(lambda: f.read(32768), b""):
                    file_hash.update(chunk)
            new_md5 = file_hash.hexdigest()
        assert md5_old == new_md5


if __name__ == "__main__":
    test_bpextract()
