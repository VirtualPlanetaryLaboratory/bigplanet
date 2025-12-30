"""
Unit tests for bpstatus module.

Tests the BigPlanet status checking functionality.
"""

import os
import pathlib
import pytest

from bigplanet import bpstatus


@pytest.fixture(autouse=True)
def preserve_cwd():
    """
    Preserve current working directory across tests.

    Many tests in this module change the working directory,
    which can break other tests that rely on os.getcwd().
    """
    original_cwd = os.getcwd()
    yield
    os.chdir(original_cwd)


class TestBpstatus:
    """Tests for bpstatus() function."""

    def test_bpstatus_checkpoint_exists(self, tempdir, checkpoint_file_in_progress, capsys):
        """
        Given: Valid checkpoint file with mixed simulation states
        When: bpstatus is called
        Then: Prints correct counts for completed, in-progress, and remaining
        """
        # Create vspace input file pointing to test folder
        pathVspaceInput = tempdir / "test.in"
        pathVspaceInput.write_text("sDestFolder test_sims\ndestfolder test_sims\n")

        # Change to tempdir so checkpoint file is found
        os.chdir(tempdir)

        # Call bpstatus
        bpstatus.bpstatus(str(pathVspaceInput))

        # Capture output
        captured = capsys.readouterr()

        # Verify output contains expected counts
        assert "Number of Simulations completed: 2" in captured.out
        assert "Number of Simulations in progress: 1" in captured.out
        assert "Number of Simulations remaining: 2" in captured.out

    def test_bpstatus_no_checkpoint(self, tempdir):
        """
        Given: No checkpoint file exists
        When: bpstatus is called
        Then: Raises Exception indicating BigPlanet must be running
        """
        # Create vspace input file
        pathVspaceInput = tempdir / "test.in"
        pathVspaceInput.write_text("sDestFolder test_sims\ndestfolder nonexistent_folder\n")

        # Change to tempdir
        os.chdir(tempdir)

        # Should raise exception
        with pytest.raises(Exception, match="BigPlanet must be running"):
            bpstatus.bpstatus(str(pathVspaceInput))

    def test_bpstatus_all_completed(self, tempdir, checkpoint_file_all_done, capsys):
        """
        Given: Checkpoint file with all simulations complete (status=1)
        When: bpstatus is called
        Then: Shows all completed, zero in-progress and remaining
        """
        # Create vspace input file
        pathVspaceInput = tempdir / "test.in"
        pathVspaceInput.write_text("sDestFolder test_sims\ndestfolder test_sims\n")

        os.chdir(tempdir)
        bpstatus.bpstatus(str(pathVspaceInput))

        captured = capsys.readouterr()
        assert "Number of Simulations completed: 3" in captured.out
        assert "Number of Simulations in progress: 0" in captured.out
        assert "Number of Simulations remaining: 0" in captured.out

    def test_bpstatus_some_in_progress(self, tempdir, checkpoint_file_in_progress, capsys):
        """
        Given: Checkpoint with mixed -1/0/1 states
        When: bpstatus is called
        Then: Correctly categorizes each state
        """
        pathVspaceInput = tempdir / "test.in"
        pathVspaceInput.write_text("sDestFolder test_sims\ndestfolder test_sims\n")

        os.chdir(tempdir)
        bpstatus.bpstatus(str(pathVspaceInput))

        captured = capsys.readouterr()
        # checkpoint_file_in_progress has: 2 done, 1 in-progress, 2 remaining
        assert "completed: 2" in captured.out
        assert "in progress: 1" in captured.out
        assert "remaining: 2" in captured.out

    def test_bpstatus_none_started(self, tempdir, checkpoint_file_none_started, capsys):
        """
        Given: Checkpoint with all status=-1 (none started)
        When: bpstatus is called
        Then: Shows zero completed, zero in-progress, all remaining
        """
        pathVspaceInput = tempdir / "test.in"
        pathVspaceInput.write_text("sDestFolder test_sims\ndestfolder test_sims\n")

        os.chdir(tempdir)
        bpstatus.bpstatus(str(pathVspaceInput))

        captured = capsys.readouterr()
        assert "Number of Simulations completed: 0" in captured.out
        assert "Number of Simulations in progress: 0" in captured.out
        assert "Number of Simulations remaining: 3" in captured.out

    def test_bpstatus_invalid_checkpoint_format(self, tempdir):
        """
        Given: Checkpoint file with malformed content
        When: bpstatus is called
        Then: Raises IndexError due to missing expected columns
        """
        # Create malformed checkpoint
        pathCheckpoint = tempdir / ".test_sims_BPL"
        pathCheckpoint.write_text("Malformed\nNo proper structure\n")

        pathVspaceInput = tempdir / "test.in"
        pathVspaceInput.write_text("sDestFolder test_sims\ndestfolder test_sims\n")

        os.chdir(tempdir)

        # Should raise IndexError when trying to access line[1]
        with pytest.raises(IndexError):
            bpstatus.bpstatus(str(pathVspaceInput))

    def test_bpstatus_empty_checkpoint(self, tempdir, checkpoint_file_empty, capsys):
        """
        Given: Empty checkpoint file
        When: bpstatus is called
        Then: Shows zero for all counts (no simulation lines to parse)
        """
        pathVspaceInput = tempdir / "test.in"
        pathVspaceInput.write_text("sDestFolder test_sims\ndestfolder test_sims\n")

        os.chdir(tempdir)
        bpstatus.bpstatus(str(pathVspaceInput))

        captured = capsys.readouterr()
        # Empty checkpoint has no simulation status lines, so all counts are 0
        assert "Number of Simulations completed: 0" in captured.out
        assert "Number of Simulations in progress: 0" in captured.out
        assert "Number of Simulations remaining: 0" in captured.out


class TestBpstatusMain:
    """Tests for main() CLI function."""

    def test_main_valid_input(self, tempdir, checkpoint_file_all_done, capsys, monkeypatch):
        """
        Given: Valid input file with existing checkpoint
        When: main() is called via CLI
        Then: Executes successfully and prints status
        """
        pathVspaceInput = tempdir / "test.in"
        pathVspaceInput.write_text("sDestFolder test_sims\ndestfolder test_sims\n")

        os.chdir(tempdir)

        # Mock sys.argv
        monkeypatch.setattr("sys.argv", ["bpstatus", str(pathVspaceInput)])

        # Call main
        bpstatus.main()

        captured = capsys.readouterr()
        assert "--BigPlanet Status--" in captured.out

    def test_main_missing_input_file(self, tempdir, monkeypatch):
        """
        Given: Input file that doesn't exist
        When: main() is called
        Then: Raises FileNotFoundError
        """
        pathVspaceInput = tempdir / "nonexistent.in"

        os.chdir(tempdir)

        monkeypatch.setattr("sys.argv", ["bpstatus", str(pathVspaceInput)])

        with pytest.raises(FileNotFoundError):
            bpstatus.main()

    def test_main_argument_parsing(self, tempdir, monkeypatch):
        """
        Given: No command-line arguments provided
        When: main() is called
        Then: argparse raises SystemExit (missing required argument)
        """
        os.chdir(tempdir)

        # Mock sys.argv with no arguments
        monkeypatch.setattr("sys.argv", ["bpstatus"])

        # argparse will raise SystemExit when required arg is missing
        with pytest.raises(SystemExit):
            bpstatus.main()
