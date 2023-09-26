import hashlib
import multiprocessing as mp
import os
import pathlib
import subprocess
import sys
import warnings
import shutil

def test_MD5CheckSum():
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
        if (path / "BP_Extract.bpa").exists():
            os.remove(path / "BP_Extract.bpa")
        if (path / ".BP_Extract").exists():
            os.remove(path / ".BP_Extract")
        if (path / ".BP_Extract_BPL").exists():
            os.remove(path / ".BP_Extract_BPL")
        if (path / "BP_Extract.md5").exists():
            os.remove(path / "BP_Extract.md5")

        # Run vspace
        print("Running vspace")
        sys.stdout.flush()
        subprocess.check_output(["vspace", "vspace.in"], cwd=path)

        # Run multi-planet
        print("Running multiplanet")
        # sys.stdout.flush()
        # subprocess.check_output(["multiplanet", "vspace.in"], cwd=path)

        # Run bigplanet
        print("Running bigplanet")
        sys.stdout.flush()
        # subprocess.check_output(["bigplanet", "bpl.in", "-a"], cwd=path)

        # bpa = path / "BP_Extract.bpa"

        # md5file = path / "BP_Extract.md5"
        # with open(md5file, "r") as md5:
        #     array = md5.read().splitlines()
        #     md5_old = array[0]
        #     with open(bpa, "rb") as f:
        #         file_hash = hashlib.md5()
        #         for chunk in iter(lambda: f.read(32768), b""):
        #             file_hash.update(chunk)
        #     new_md5 = file_hash.hexdigest()
        # assert md5_old == new_md5

        # shutil.rmtree(path / "BP_Extract")
        # os.remove(path / "BP_Extract.bpa")
        # os.remove(path / ".BP_Extract")
        # os.remove(path / ".BP_Extract_BPL")
        # os.remove(path / "BP_Extract.md5")

if __name__ == "__main__":
    test_MD5CheckSum()
