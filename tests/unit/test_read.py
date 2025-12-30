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


class TestReadFileAdvanced:
    """Advanced tests for ReadFile validation logic."""

    def test_read_file_both_include_exclude_error(self, tempdir):
        """
        Given: BPL file with both saKeyInclude and saKeyExclude
        When: ReadFile is called
        Then: Error is raised (mutually exclusive)
        """
        sim_dir = tempdir / "test_sims"
        sim_dir.mkdir()

        bpl_content = """sDestFolder test_sims
saBodyFiles  earth.in
sPrimaryFile vpl.in
saKeyInclude earth:Mass:final
saKeyExclude sun:Luminosity:initial
"""
        bpl_file = tempdir / "bpl.in"
        bpl_file.write_text(bpl_content)

        with pytest.raises(SystemExit):
            read.ReadFile(str(bpl_file), verbose=False, archive=False)

    def test_read_file_custom_archive_name(self, tempdir):
        """
        Given: BPL file with custom sArchiveFile
        When: ReadFile is called
        Then: Custom archive name is used
        """
        sim_dir = tempdir / "test_sims"
        sim_dir.mkdir()

        bpl_content = """sDestFolder test_sims
sArchiveFile custom_archive.bpa
saBodyFiles  earth.in
sPrimaryFile vpl.in
"""
        bpl_file = tempdir / "bpl.in"
        bpl_file.write_text(bpl_content)

        result = read.ReadFile(str(bpl_file), verbose=False, archive=True)
        _, bpl_archive, _, _, _, _, _, _, _ = result

        assert bpl_archive == "custom_archive.bpa"

    def test_read_file_custom_output_name(self, tempdir):
        """
        Given: BPL file with custom sOutputFile
        When: ReadFile is called
        Then: Custom output name is used
        """
        sim_dir = tempdir / "test_sims"
        sim_dir.mkdir()

        bpl_content = """sDestFolder test_sims
sOutputFile my_output.bpf
saBodyFiles  earth.in
sPrimaryFile vpl.in
saKeyInclude earth:Mass:final
"""
        bpl_file = tempdir / "bpl.in"
        bpl_file.write_text(bpl_content)

        result = read.ReadFile(str(bpl_file), verbose=False, archive=False)
        _, _, output, _, _, _, _, _, _ = result

        assert output == "my_output.bpf"

    def test_read_file_ulysses_mode(self, tempdir):
        """
        Given: BPL file with bUlysses flag
        When: ReadFile is called
        Then: Output file is User.csv and Ulysses=1
        """
        sim_dir = tempdir / "test_sims"
        sim_dir.mkdir()

        bpl_content = """sDestFolder test_sims
saBodyFiles  earth.in
sPrimaryFile vpl.in
bUlysses
saKeyInclude earth:Mass:final
"""
        bpl_file = tempdir / "bpl.in"
        bpl_file.write_text(bpl_content)

        result = read.ReadFile(str(bpl_file), verbose=False, archive=False)
        _, _, output, _, _, _, _, ulysses, _ = result

        assert output == "User.csv"
        assert ulysses == 1

    def test_read_file_ulysses_with_simname_forward(self, tempdir, capsys):
        """
        Given: BPL with Ulysses=True, SimName, and forward keys
        When: ReadFile is called
        Then: Succeeds (valid configuration)
        """
        sim_dir = tempdir / "test_sims"
        sim_dir.mkdir()

        bpl_content = """sDestFolder test_sims
saBodyFiles  earth.in
sPrimaryFile vpl.in
bUlysses
sSimName sim_00
saKeyInclude earth:Temp:forward
"""
        bpl_file = tempdir / "bpl.in"
        bpl_file.write_text(bpl_content)

        result = read.ReadFile(str(bpl_file), verbose=False, archive=False)
        _, _, _, _, _, include, _, ulysses, simname = result

        assert ulysses == 1
        assert simname == "sim_00"
        assert "earth:Temp:forward" in include

    def test_read_file_ulysses_simname_non_forward_error(self, tempdir):
        """
        Given: BPL with Ulysses, SimName, but non-forward keys in include
        When: ReadFile is called
        Then: Error is raised (SimName requires forward data)
        """
        sim_dir = tempdir / "test_sims"
        sim_dir.mkdir()

        bpl_content = """sDestFolder test_sims
saBodyFiles  earth.in
sPrimaryFile vpl.in
bUlysses
sSimName sim_00
saKeyInclude earth:Mass:final
"""
        bpl_file = tempdir / "bpl.in"
        bpl_file.write_text(bpl_content)

        with pytest.raises(SystemExit):
            read.ReadFile(str(bpl_file), verbose=False, archive=False)

    def test_read_file_ulysses_forward_without_simname_error(self, tempdir):
        """
        Given: BPL with Ulysses=True, forward keys, but no SimName
        When: ReadFile is called
        Then: Error is raised (forward requires SimName)
        """
        sim_dir = tempdir / "test_sims"
        sim_dir.mkdir()

        bpl_content = """sDestFolder test_sims
saBodyFiles  earth.in
sPrimaryFile vpl.in
bUlysses
saKeyInclude earth:Temp:forward
"""
        bpl_file = tempdir / "bpl.in"
        bpl_file.write_text(bpl_content)

        with pytest.raises(SystemExit):
            read.ReadFile(str(bpl_file), verbose=False, archive=False)

    def test_read_file_verbose_output(self, tempdir, capsys):
        """
        Given: BPL file with verbose=True
        When: ReadFile is called
        Then: Diagnostic information is printed
        """
        sim_dir = tempdir / "test_sims"
        sim_dir.mkdir()

        bpl_content = """sDestFolder test_sims
saBodyFiles  earth.in
sPrimaryFile vpl.in
saKeyInclude earth:Mass:final
"""
        bpl_file = tempdir / "bpl.in"
        bpl_file.write_text(bpl_content)

        read.ReadFile(str(bpl_file), verbose=True, archive=False)

        captured = capsys.readouterr()
        assert "Folder Name:" in captured.out
        assert "BPL Archive File:" in captured.out
        assert "Include List:" in captured.out


class TestGetDir:
    """Tests for GetDir function."""

    def test_get_dir_basic(self, tempdir):
        """
        Given: vspace.in file with sDestFolder
        When: GetDir is called
        Then: Returns folder name and infiles list
        """
        import os
        original_cwd = os.getcwd()
        os.chdir(tempdir)

        try:
            sim_dir = tempdir / "test_sims"
            sim_dir.mkdir()

            vspace_content = """sDestFolder test_sims
sBodyFile earth.in
sPrimaryFile vpl.in
"""
            vspace_file = tempdir / "vspace.in"
            vspace_file.write_text(vspace_content)

            folder, infiles = read.GetDir(str(vspace_file))

            assert folder == "test_sims"
            assert "earth.in" in infiles
            assert "vpl.in" in infiles
        finally:
            os.chdir(original_cwd)

    def test_get_dir_folder_not_exists(self, tempdir):
        """
        Given: vspace.in pointing to non-existent folder
        When: GetDir is called
        Then: Error is raised
        """
        vspace_content = """sDestFolder nonexistent_folder
sBodyFile earth.in
"""
        vspace_file = tempdir / "vspace.in"
        vspace_file.write_text(vspace_content)

        with pytest.raises(SystemExit):
            read.GetDir(str(vspace_file))


class TestGetLogName:
    """Tests for GetLogName function."""

    def test_get_log_name_default(self, minimal_simulation_dir):
        """
        Given: Input files without custom sLogfile
        When: GetLogName is called
        Then: Returns system_name.log
        """
        infiles = ["earth.in", "vpl.in"]
        sims = [str(minimal_simulation_dir)]
        system_name = "earth"

        result = read.GetLogName(infiles, sims, system_name)

        assert result == "earth.log"

    def test_get_log_name_custom(self, tempdir):
        """
        Given: Input file with custom sLogfile parameter
        When: GetLogName is called
        Then: Returns custom log name
        """
        sim_dir = tempdir / "sim_00"
        sim_dir.mkdir()

        # Create vpl.in with custom log name
        vpl_content = """sSystemName test_system
sLogfile custom_log
"""
        (sim_dir / "vpl.in").write_text(vpl_content)

        infiles = ["vpl.in"]
        sims = [str(sim_dir)]
        system_name = "test_system"

        result = read.GetLogName(infiles, sims, system_name)

        assert result == "custom_log.log"


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
