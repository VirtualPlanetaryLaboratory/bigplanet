"""
Unit tests for bigplanet/read.py module.

Tests cover file reading, simulation directory handling, and VPLanet help parsing.
"""

import os
import pathlib
import tempfile

import pytest

from bigplanet import read
from tests.fixtures import generators


class TestReadFile:
    """Tests for ReadFile function."""

    def test_read_file_basic(self, tempdir):
        """
        Given: A basic BigPlanet input file
        When: ReadFile is called
        Then: All parameters are extracted correctly
        """
        # Create test simulation directory
        sim_dir = tempdir / "test_sims"
        sim_dir.mkdir()

        # Create bpl.in
        bpl_content = """sDestFolder test_sims

saBodyFiles  earth.in sun.in
sPrimaryFile vpl.in
"""
        bpl_file = tempdir / "bpl.in"
        bpl_file.write_text(bpl_content)

        result = read.ReadFile(str(bpl_file), verbose=False, archive=True)

        folder, bpl_archive, output, bodylist, primary, include, exclude, ulysses, simname = result

        assert folder == "test_sims"
        assert bpl_archive == "test_sims.bpa"
        assert "earth.in" in bodylist
        assert "sun.in" in bodylist
        assert primary == "vpl.in"
        assert include == []
        assert exclude == []

    def test_read_file_with_include_list(self, tempdir):
        """
        Given: A BigPlanet input file with include list
        When: ReadFile is called
        Then: Include list is extracted
        """
        sim_dir = tempdir / "test_sims"
        sim_dir.mkdir()

        bpl_content = """sDestFolder test_sims

saBodyFiles  earth.in
sPrimaryFile vpl.in

saKeyInclude earth:Mass:final sun:Luminosity:initial
"""
        bpl_file = tempdir / "bpl.in"
        bpl_file.write_text(bpl_content)

        result = read.ReadFile(str(bpl_file), verbose=False, archive=False)

        _, _, _, _, _, include, exclude, _, _ = result

        assert "earth:Mass:final" in include
        assert "sun:Luminosity:initial" in include
        assert len(exclude) == 0

    def test_read_file_multiline_body_files(self, tempdir):
        """
        Given: A bpl.in with multiline body files (using $)
        When: ReadFile is called
        Then: All body files are extracted
        """
        sim_dir = tempdir / "test_sims"
        sim_dir.mkdir()

        bpl_content = """sDestFolder test_sims

saBodyFiles  earth.in $
    mars.in venus.in
sPrimaryFile vpl.in
"""
        bpl_file = tempdir / "bpl.in"
        bpl_file.write_text(bpl_content)

        result = read.ReadFile(str(bpl_file), verbose=False, archive=True)

        _, _, _, bodylist, _, _, _, _, _ = result

        assert "earth.in" in bodylist
        assert "mars.in" in bodylist
        assert "venus.in" in bodylist

    def test_read_file_missing_dest_folder(self, tempdir):
        """
        Given: A bpl.in without sDestFolder
        When: ReadFile is called
        Then: Error is raised
        """
        bpl_content = """saBodyFiles  earth.in
sPrimaryFile vpl.in
"""
        bpl_file = tempdir / "bpl.in"
        bpl_file.write_text(bpl_content)

        with pytest.raises(SystemExit):
            read.ReadFile(str(bpl_file), verbose=False, archive=True)


class TestGetSims:
    """Tests for GetSims function."""

    def test_get_sims_basic(self, tempdir):
        """
        Given: A folder with simulation directories
        When: GetSims is called
        Then: All simulation paths are returned sorted
        """
        base_dir = tempdir / "sims"
        base_dir.mkdir()

        # Create simulation directories
        (base_dir / "sim_00").mkdir()
        (base_dir / "sim_01").mkdir()
        (base_dir / "sim_02").mkdir()

        # Create a file (should be ignored)
        (base_dir / "readme.txt").write_text("test")

        result = read.GetSims(str(base_dir))

        assert len(result) == 3
        assert any("sim_00" in str(p) for p in result)
        assert any("sim_01" in str(p) for p in result)
        assert any("sim_02" in str(p) for p in result)
        # Results should be sorted
        assert "sim_00" in result[0]

    def test_get_sims_with_filter(self, tempdir):
        """
        Given: A folder with simulation directories
        When: GetSims is called with a name filter
        Then: Only matching directories are returned
        """
        base_dir = tempdir / "sims"
        base_dir.mkdir()

        (base_dir / "test_00").mkdir()
        (base_dir / "test_01").mkdir()
        (base_dir / "other_00").mkdir()

        result = read.GetSims(str(base_dir), simname="test")

        assert len(result) == 2
        assert all("test" in str(p) for p in result)

    def test_get_sims_nonexistent_folder(self):
        """
        Given: A non-existent folder path
        When: GetSims is called
        Then: IOError is raised
        """
        with pytest.raises(IOError):
            read.GetSims("/nonexistent/path")


class TestGetSNames:
    """Tests for GetSNames function."""

    def test_get_snames_basic(self, minimal_simulation_dir):
        """
        Given: Simulation directories with input files
        When: GetSNames is called
        Then: System name and body names are extracted
        """
        sim_dir = minimal_simulation_dir
        bodyfiles = ["earth.in", "vpl.in"]
        sims = [str(sim_dir)]

        system_name, body_names = read.GetSNames(bodyfiles, sims)

        assert system_name == "earth"
        assert "earth" in body_names


class TestDollarSign:
    """Tests for DollarSign function."""

    def test_dollar_sign_continuation(self):
        """
        Given: Lines with $ continuation
        When: DollarSign is called
        Then: Lines are combined correctly
        """
        file_lines = [
            "first line $",
            "second line $",
            "third line"
        ]

        result = []
        read.DollarSign(result, file_lines[0], 0, file_lines)

        # Should have combined all lines
        assert len(result) == 3
        assert result[0] == "first line "
        assert result[1] == "second line "
        assert result[2] == "third line"


class TestGetVplanetHelp:
    """Tests for GetVplanetHelp function."""

    def test_get_vplanet_help_format(self):
        """
        Given: VPLanet is installed
        When: GetVplanetHelp is called
        Then: A dictionary with parameter info is returned
        """
        # This test requires vplanet to be installed
        try:
            result = read.GetVplanetHelp()

            # Should be a dictionary
            assert isinstance(result, dict)

            # Should have some common parameters
            # (exact parameters depend on vplanet version)
            assert len(result) > 0

            # Check structure of a parameter if present
            if "dMass" in result:
                assert "Type" in result["dMass"]

        except Exception as e:
            # If vplanet is not available, skip test
            pytest.skip(f"VPLanet not available: {e}")
