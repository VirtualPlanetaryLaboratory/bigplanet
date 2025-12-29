import multiprocessing as mp
import os
import pathlib
import subprocess
import sys
import warnings
import shutil
import h5py

def test_Fletcher32CheckSum():
    """
    Test that HDF5 datasets are created with Fletcher32 checksums enabled.

    This replaces the old MD5 checksum test. Fletcher32 is HDF5's built-in
    checksum mechanism that provides per-dataset data integrity verification,
    which is more reliable than file-level MD5 checksums for HDF5 files.
    """
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

        # Run vspace
        print("Running vspace")
        sys.stdout.flush()
        subprocess.check_output(["vspace", "vspace.in"], cwd=path)

        # Run multi-planet
        print("Running multiplanet")
        sys.stdout.flush()
        subprocess.check_output(["multiplanet", "vspace.in"], cwd=path)

        # Run bigplanet
        print("Running bigplanet")
        sys.stdout.flush()
        subprocess.check_output(["bigplanet", "bpl.in", "-a"], cwd=path)

        bpa = path / "BP_Extract.bpa"

        # Verify that non-scalar datasets have Fletcher32 checksums enabled
        # Note: Fletcher32 only works on datasets with at least one dimension (not scalars)
        with h5py.File(bpa, "r") as f:
            # Get first simulation group
            first_group = list(f.keys())[0]
            group = f[first_group]

            # Find a non-scalar dataset to test (scalars can't have Fletcher32)
            test_dataset_name = None
            for dataset_name in group.keys():
                dataset = group[dataset_name]
                if dataset.ndim > 0:  # Non-scalar dataset
                    test_dataset_name = dataset_name
                    break

            assert test_dataset_name is not None, "No non-scalar datasets found to test"

            dataset = group[test_dataset_name]

            # Check if Fletcher32 filter is in the filter pipeline
            plist = dataset.id.get_create_plist()
            nfilters = plist.get_nfilters()

            # Check each filter to see if Fletcher32 is present
            has_fletcher32 = False
            for i in range(nfilters):
                filter_info = plist.get_filter(i)
                if filter_info[0] == h5py.h5z.FILTER_FLETCHER32:
                    has_fletcher32 = True
                    break

            assert has_fletcher32, f"Fletcher32 checksum should be enabled on non-scalar dataset {test_dataset_name}"
            print(f"Verified: Fletcher32 checksum enabled on dataset {first_group}/{test_dataset_name}")

        shutil.rmtree(path / "BP_Extract")
        os.remove(path / "BP_Extract.bpa")
        os.remove(path / ".BP_Extract")
        os.remove(path / ".BP_Extract_BPL")

if __name__ == "__main__":
    test_Fletcher32CheckSum()
