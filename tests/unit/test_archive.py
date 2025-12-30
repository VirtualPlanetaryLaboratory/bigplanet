"""
Unit tests for archive module.

Tests the BigPlanet archive creation functionality, including checkpoint
management and multiprocessing worker functions.
"""

import multiprocessing as mp
import os
import pathlib
import pytest
import h5py
import numpy as np

from bigplanet import archive


class TestCreateCP:
    """Tests for CreateCP() function."""

    def test_create_checkpoint_basic(self, tempdir):
        """
        Given: Checkpoint file path, input file, and simulation list
        When: CreateCP is called
        Then: Creates checkpoint file with correct format
        """
        sCheckpointFile = str(tempdir / ".test_BPL")
        sInputFile = "test.in"
        listSims = ["sim_00", "sim_01", "sim_02"]

        archive.CreateCP(sCheckpointFile, sInputFile, listSims)

        assert os.path.exists(sCheckpointFile)

        with open(sCheckpointFile, "r") as f:
            lines = f.readlines()

        # Verify format
        assert "Vspace File:" in lines[0]
        assert "test.in" in lines[0]
        assert "Total Number of Simulations: 3" in lines[1]
        assert "sim_00 -1" in lines[2]
        assert "sim_01 -1" in lines[3]
        assert "sim_02 -1" in lines[4]
        assert "THE END" in lines[5]

    def test_create_checkpoint_many_sims(self, tempdir):
        """
        Given: Large simulation list (100+ simulations)
        When: CreateCP is called
        Then: Creates checkpoint with all simulations marked as -1
        """
        sCheckpointFile = str(tempdir / ".large_BPL")
        sInputFile = "test.in"
        listSims = [f"sim_{i:03d}" for i in range(100)]

        archive.CreateCP(sCheckpointFile, sInputFile, listSims)

        with open(sCheckpointFile, "r") as f:
            lines = f.readlines()

        assert len(lines) == 103  # header(2) + sims(100) + footer(1)
        assert "Total Number of Simulations: 100" in lines[1]

        # Check all marked as -1
        for i in range(100):
            assert f"sim_{i:03d} -1" in lines[i + 2]


class TestReCreateCP:
    """Tests for ReCreateCP() function."""

    def test_recreate_all_done_no_force(self, tempdir, checkpoint_file_all_done):
        """
        Given: Checkpoint with all simulations complete (status=1), force=False
        When: ReCreateCP is called
        Then: Exits without recreating checkpoint
        """
        # Create dummy archive file
        pathArchive = tempdir / "test_sims.bpa"
        with h5py.File(pathArchive, "w") as f:
            f.create_group("sim_00")

        # Should exit
        with pytest.raises(SystemExit):
            archive.ReCreateCP(
                str(checkpoint_file_all_done),
                "test.in",
                quiet=True,
                sims=["sim_00", "sim_01", "sim_02"],
                folder_name=str(tempdir / "test_sims"),
                force=False
            )

    def test_recreate_force_rebuild(self, tempdir, checkpoint_file_all_done):
        """
        Given: Checkpoint with all done, force=True
        When: ReCreateCP is called
        Then: Deletes BPA file and recreates checkpoint
        """
        pathArchive = tempdir / "test_sims.bpa"
        with h5py.File(pathArchive, "w") as f:
            f.create_group("sim_00")

        assert pathArchive.exists()

        archive.ReCreateCP(
            str(checkpoint_file_all_done),
            "test.in",
            quiet=True,
            sims=["sim_00", "sim_01", "sim_02"],
            folder_name=str(tempdir / "test_sims"),
            force=True
        )

        # BPA file should be deleted
        assert not pathArchive.exists()

        # Checkpoint should be recreated with all -1
        with open(checkpoint_file_all_done, "r") as f:
            lines = f.readlines()
            assert "sim_00 -1" in lines[2]

    def test_recreate_failed_sims(self, tempdir):
        """
        Given: Checkpoint with some status=0 (in-progress failures)
        When: ReCreateCP is called
        Then: Changes 0 to -1 and removes corresponding groups from HDF5
        """
        # Create checkpoint with mixed states
        pathCheckpoint = tempdir / ".test_BPL"
        with open(pathCheckpoint, "w") as f:
            f.write(f"Vspace File: {tempdir}/test.in\n")
            f.write("Total Number of Simulations: 3\n")
            f.write("sim_00 1\n")
            f.write("sim_01 0\n")  # Failed
            f.write("sim_02 -1\n")
            f.write("THE END\n")

        # Create archive with groups
        pathArchive = tempdir / "test_sims.bpa"
        with h5py.File(pathArchive, "w") as f:
            f.create_group("/sim_00")
            f.create_group("/sim_01")  # Should be deleted

        archive.ReCreateCP(
            str(pathCheckpoint),
            "test.in",
            quiet=True,
            sims=["sim_00", "sim_01", "sim_02"],
            folder_name=str(tempdir / "test_sims"),
            force=False
        )

        # Verify checkpoint updated
        with open(pathCheckpoint, "r") as f:
            lines = f.readlines()
            assert "sim_01 -1" in lines[3]  # Changed from 0 to -1

        # Verify group deleted from HDF5
        with h5py.File(pathArchive, "r") as f:
            assert "/sim_00" in f  # Completed, kept
            assert "/sim_01" not in f  # Failed, deleted


class TestCheckpointHelpers:
    """Tests for checkpoint helper functions."""

    def test_get_next_simulation_first(self, tempdir, checkpoint_file_in_progress):
        """
        Given: Checkpoint with first simulation available (-1)
        When: fnGetNextSimulation is called
        Then: Returns first simulation and marks as in-progress (0)
        """
        lock = mp.Lock()

        sFolder = archive.fnGetNextSimulation(str(checkpoint_file_in_progress), lock)

        assert sFolder is not None
        assert "sim_02" in sFolder  # First -1 in checkpoint_file_in_progress

        # Verify marked as 0
        with open(checkpoint_file_in_progress, "r") as f:
            lines = f.readlines()
            # sim_02 was -1, should now be 0
            assert "sim_02 0" in lines[4]

    def test_get_next_simulation_none_left(self, tempdir, checkpoint_file_all_done):
        """
        Given: Checkpoint with all simulations complete
        When: fnGetNextSimulation is called
        Then: Returns None
        """
        lock = mp.Lock()

        sFolder = archive.fnGetNextSimulation(str(checkpoint_file_all_done), lock)

        assert sFolder is None

    def test_mark_simulation_complete(self, tempdir, checkpoint_file_in_progress):
        """
        Given: Checkpoint with simulation in progress
        When: fnMarkSimulationComplete is called
        Then: Updates status to 1
        """
        lock = mp.Lock()

        # Get the first in-progress simulation
        with open(checkpoint_file_in_progress, "r") as f:
            lines = f.readlines()
            # Find first simulation
            sFolder = lines[2].split()[0]

        archive.fnMarkSimulationComplete(
            str(checkpoint_file_in_progress),
            sFolder,
            lock
        )

        # Verify marked as 1
        with open(checkpoint_file_in_progress, "r") as f:
            lines = f.readlines()
            assert f"{sFolder} 1" in lines[2]

    def test_check_group_exists_true(self, tempdir):
        """
        Given: HDF5 file with existing group
        When: fbCheckGroupExists is called
        Then: Returns True
        """
        pathArchive = tempdir / "test.bpa"
        with h5py.File(pathArchive, "w") as f:
            f.create_group("/sim_00")

        with h5py.File(pathArchive, "r") as f:
            bExists = archive.fbCheckGroupExists(f, "/sim_00")

        assert bExists is True

    def test_check_group_exists_false(self, tempdir):
        """
        Given: HDF5 file without group
        When: fbCheckGroupExists is called
        Then: Returns False
        """
        pathArchive = tempdir / "test.bpa"
        with h5py.File(pathArchive, "w") as f:
            f.create_group("/sim_00")

        with h5py.File(pathArchive, "r") as f:
            bExists = archive.fbCheckGroupExists(f, "/sim_01")

        assert bExists is False


class TestProcessSimulationData:
    """Tests for fnProcessSimulationData() function."""

    def test_process_simulation_basic(self, tempdir, minimal_simulation_dir,
                                      sample_vplanet_help_dict):
        """
        Given: Valid simulation directory
        When: fnProcessSimulationData is called
        Then: Returns dictionary with simulation data
        """
        dictData = archive.fnProcessSimulationData(
            str(minimal_simulation_dir),
            "earth",
            ["earth"],
            "earth.log",
            ["earth.in", "vpl.in"],
            sample_vplanet_help_dict,
            False  # bVerbose - positional argument
        )

        assert isinstance(dictData, dict)
        assert len(dictData) > 0
        # Should contain keys from log file processing
        assert any("earth" in key for key in dictData.keys())


class TestWriteSimulationToArchive:
    """Tests for fnWriteSimulationToArchive() function."""

    def test_write_simulation_to_archive(self, tempdir, sample_vplanet_help_dict):
        """
        Given: Data dictionary and HDF5 file handle
        When: fnWriteSimulationToArchive is called
        Then: Writes data to HDF5 group
        """
        pathArchive = tempdir / "test.bpa"

        dictData = {
            "earth:Mass:initial": np.array([5.972e24]),
            "earth:Mass:final": np.array([5.972e24]),
        }

        with h5py.File(pathArchive, "w") as f:
            archive.fnWriteSimulationToArchive(
                f,
                dictData,
                "/sim_00",
                sample_vplanet_help_dict,
                False  # bVerbose - positional argument
            )

        # Verify data written
        with h5py.File(pathArchive, "r") as f:
            assert "/sim_00" in f
            grp = f["/sim_00"]
            assert "earth:Mass:initial" in grp
            assert "earth:Mass:final" in grp


# TODO: Add integration tests for Archive() function
# These require more complex setup with proper simulation directories
# and BPL input files. The helper functions are already well-tested above.
