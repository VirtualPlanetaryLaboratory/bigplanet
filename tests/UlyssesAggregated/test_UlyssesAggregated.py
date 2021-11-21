import subprocess
import numpy as np
import os
import pathlib
import warnings
import csv
import multiprocessing as mp
import sys
import bigplanet.bp_extract as bp


def test_ulyssesaggregated():
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
        if not (path / "User.csv").exists():
            subprocess.check_output(["bigplanet", "bpl.in"], cwd=path)

        file = path / "User.csv"

        data = bp.CSVToDict(file, 1)
        assert np.isclose(
            float(data['earth:Instellation:final'][0]), 1367.635318)


if __name__ == "__main__":
    test_ulyssesaggregated()
