"""
Unit tests for bigplanet/process.py module.

Tests cover all data processing functions including log file parsing,
input file parsing, output file processing, and data aggregation.
"""

import os
import pathlib
import tempfile

import h5py
import numpy as np
import pytest

from bigplanet import process
from tests.fixtures import generators


class TestProcessLogFile:
    """Tests for ProcessLogFile function."""

    def test_process_log_file_basic(self, minimal_vplanet_log, sample_vplanet_help_dict):
        """
        Given: A minimal VPLanet log file
        When: ProcessLogFile is called
        Then: All initial and final parameters are extracted correctly
        """
        data = {}
        folder = minimal_vplanet_log.parent
        logfile = minimal_vplanet_log.name

        result = process.ProcessLogFile(
            logfile, data, str(folder), verbose=False
        )

        # Check that data was populated
        assert len(result) > 0

        # Check initial system properties
        assert "system:Age:initial" in result
        assert result["system:Age:initial"][0] == "sec"
        assert float(result["system:Age:initial"][1]) == 0.0

        # Check final sun properties
        assert "sun:Mass:final" in result
        assert result["sun:Mass:final"][0] == "kg"
        assert float(result["sun:Mass:final"][1]) == pytest.approx(1.988416e+30)

        # Check earth properties
        assert "earth:Mass:final" in result
        assert float(result["earth:Mass:final"][1]) == pytest.approx(5.972e+24)

        assert "earth:Obliquity:final" in result
        assert float(result["earth:Obliquity:final"][1]) == pytest.approx(0.408407)

    def test_process_log_file_with_include_list(self, minimal_vplanet_log):
        """
        Given: A log file and an include list
        When: ProcessLogFile is called with include list
        Then: Only included keys are extracted
        """
        data = {}
        folder = minimal_vplanet_log.parent
        logfile = minimal_vplanet_log.name

        include_list = ["earth:Mass:final", "sun:Luminosity:final"]

        result = process.ProcessLogFile(
            logfile, data, str(folder), verbose=False, incl=include_list
        )

        # Check that only included keys are present
        assert "earth:Mass:final" in result
        assert "sun:Luminosity:final" in result

        # Check that non-included keys are not present
        assert "earth:Obliquity:final" not in result
        assert "sun:Mass:final" not in result

    def test_process_log_file_output_order(self, minimal_vplanet_log):
        """
        Given: A log file with OutputOrder
        When: ProcessLogFile is called
        Then: OutputOrder is correctly extracted with units
        """
        data = {}
        folder = minimal_vplanet_log.parent
        logfile = minimal_vplanet_log.name

        result = process.ProcessLogFile(
            logfile, data, str(folder), verbose=False
        )

        # Check OutputOrder for earth
        assert "earth:OutputOrder" in result
        output_order = result["earth:OutputOrder"]

        # OutputOrder should be a list of [variable, unit] pairs
        assert isinstance(output_order, list)
        assert len(output_order) > 0

        # Check that Time and TMan are in the output order
        var_names = [item[0] for item in output_order]
        assert "Time" in var_names
        assert "TMan" in var_names

    def test_process_log_file_verbose(self, minimal_vplanet_log, capsys):
        """
        Given: A log file
        When: ProcessLogFile is called with verbose=True
        Then: File path is printed
        """
        data = {}
        folder = minimal_vplanet_log.parent
        logfile = minimal_vplanet_log.name

        process.ProcessLogFile(
            logfile, data, str(folder), verbose=True
        )

        captured = capsys.readouterr()
        assert str(minimal_vplanet_log) in captured.out

    def test_process_log_file_missing_file(self):
        """
        Given: A non-existent log file path
        When: ProcessLogFile is called
        Then: FileNotFoundError is raised
        """
        data = {}
        with pytest.raises(FileNotFoundError):
            process.ProcessLogFile(
                "nonexistent.log", data, "/tmp", verbose=False
            )

    def test_process_log_file_empty_data_initial(self, minimal_vplanet_log):
        """
        Given: An empty data dictionary
        When: ProcessLogFile is called
        Then: Data is populated without errors
        """
        data = {}
        folder = minimal_vplanet_log.parent
        logfile = minimal_vplanet_log.name

        result = process.ProcessLogFile(
            logfile, data, str(folder), verbose=False
        )

        assert isinstance(result, dict)
        assert len(result) > 0

    def test_process_log_file_existing_data(self, minimal_vplanet_log):
        """
        Given: A data dictionary with existing keys
        When: ProcessLogFile is called
        Then: New values are appended to existing keys
        """
        data = {"earth:Mass:final": ["kg", "1.0e24"]}
        folder = minimal_vplanet_log.parent
        logfile = minimal_vplanet_log.name

        result = process.ProcessLogFile(
            logfile, data, str(folder), verbose=False
        )

        # Check that the new value was appended
        assert len(result["earth:Mass:final"]) == 3
        assert result["earth:Mass:final"][0] == "kg"
        assert result["earth:Mass:final"][1] == "1.0e24"


class TestProcessInputfile:
    """Tests for ProcessInputfile function."""

    def test_process_input_file_basic(self, minimal_vplanet_input, sample_vplanet_help_dict):
        """
        Given: A minimal VPLanet input file
        When: ProcessInputfile is called
        Then: All parameters are extracted correctly
        """
        data = {}
        folder = minimal_vplanet_input.parent
        infile = minimal_vplanet_input.name

        result = process.ProcessInputfile(
            data, infile, str(folder), sample_vplanet_help_dict, verbose=False
        )

        # Check that parameters were extracted
        assert "earth:sName:option" in result
        assert result["earth:sName:option"][1] == "earth"

        assert "earth:dMass:option" in result
        assert result["earth:dMass:option"][1] == "-1.0"

        assert "earth:dObliquity:option" in result
        assert result["earth:dObliquity:option"][1] == "23.5"

    def test_process_input_file_with_include_list(self, minimal_vplanet_input, sample_vplanet_help_dict):
        """
        Given: An input file and include list
        When: ProcessInputfile is called with include list
        Then: Only included parameters are extracted
        """
        data = {}
        folder = minimal_vplanet_input.parent
        infile = minimal_vplanet_input.name

        include_list = ["earth:dMass:option", "earth:dObliquity:option"]

        result = process.ProcessInputfile(
            data, infile, str(folder), sample_vplanet_help_dict,
            verbose=False, incl=include_list
        )

        # Check included keys
        assert "earth:dMass:option" in result
        assert "earth:dObliquity:option" in result

        # Check excluded keys
        assert "earth:sName:option" not in result
        assert "earth:dRadius:option" not in result

    def test_process_input_file_line_continuation(self, tempdir, sample_vplanet_help_dict, minimal_vpl_input):
        """
        Given: An input file with line continuation ($)
        When: ProcessInputfile is called
        Then: First value is extracted (current behavior)

        Note: Current production code limitation - ProcessInputfile only extracts
        the first value (line[1]) from multi-value parameters. Line continuation
        is handled by DollarSign in read.py but ProcessInputfile splits on whitespace
        and takes only index [1]. This test documents current behavior.
        """
        # Create input file with line continuation
        content = """sName earth
saOutputOrder -Time -TMan $
    -TCore -Obliquity
"""
        input_file = tempdir / "earth.in"
        input_file.write_text(content)

        data = {}
        result = process.ProcessInputfile(
            data, "earth.in", str(tempdir), sample_vplanet_help_dict, verbose=False
        )

        # Currently only extracts first value due to line[1] indexing
        assert "earth:saOutputOrder:option" in result
        value = result["earth:saOutputOrder:option"][1]
        # Leading dashes are stripped by production code (process.py lines 321-324)
        assert value == "Time"  # Only first parameter extracted

    def test_process_input_file_comments_ignored(self, tempdir, sample_vplanet_help_dict, minimal_vpl_input):
        """
        Given: An input file with comments
        When: ProcessInputfile is called
        Then: Comments are ignored, only parameters extracted
        """
        content = """# This is a comment
sName earth  # inline comment
# Another comment
dMass -1.0
"""
        input_file = tempdir / "earth.in"
        input_file.write_text(content)

        data = {}
        result = process.ProcessInputfile(
            data, "earth.in", str(tempdir), sample_vplanet_help_dict, verbose=False
        )

        assert "earth:sName:option" in result
        assert result["earth:sName:option"][1] == "earth"
        assert "earth:dMass:option" in result


class TestProcessInfileUnits:
    """Tests for ProcessInfileUnits function."""

    def test_process_infile_units_with_custom_unit(self, minimal_vplanet_input, sample_vplanet_help_dict):
        """
        Given: A parameter with negative value and custom unit
        When: ProcessInfileUnits is called
        Then: Custom unit is returned
        """
        folder = minimal_vplanet_input.parent
        infile = str(minimal_vplanet_input)

        # dSemi has custom unit "AU" when negative
        units = process.ProcessInfileUnits(
            "dSemi", "-1.0", str(folder), infile, sample_vplanet_help_dict
        )

        assert units == "AU"

    def test_process_infile_units_dimensionless(self, minimal_vplanet_input, sample_vplanet_help_dict):
        """
        Given: A dimensionless parameter
        When: ProcessInfileUnits is called
        Then: "nd" (no dimension) is returned
        """
        folder = minimal_vplanet_input.parent
        infile = str(minimal_vplanet_input)

        # Create a help dict entry with no dimension
        help_dict = sample_vplanet_help_dict.copy()
        help_dict["dTestParam"] = {"Dimension": "nd"}

        units = process.ProcessInfileUnits(
            "dTestParam", "1.0", str(folder), infile, help_dict
        )

        assert units == "nd"

    def test_process_infile_units_from_input_file(self, tempdir, sample_vplanet_help_dict):
        """
        Given: A parameter with units specified in input file
        When: ProcessInfileUnits is called
        Then: Unit from input file is used
        """
        # Create vpl.in (required by ProcessInfileUnits)
        vpl_content = """sSystemName test
sUnitMass kg
sUnitLength m
"""
        vpl_file = tempdir / "vpl.in"
        vpl_file.write_text(vpl_content)

        # Create input file with unit specification
        content = """sUnitMass solar
dMass 1.0
"""
        input_file = tempdir / "test.in"
        input_file.write_text(content)

        units = process.ProcessInfileUnits(
            "dMass", "1.0", str(tempdir), str(input_file),
            sample_vplanet_help_dict
        )

        assert "solar" in units

    def test_process_infile_units_default(self, minimal_vplanet_input, sample_vplanet_help_dict):
        """
        Given: A parameter without explicit unit specification
        When: ProcessInfileUnits is called
        Then: Default unit is returned
        """
        folder = minimal_vplanet_input.parent
        infile = str(minimal_vplanet_input)

        # dMass should get default unit
        units = process.ProcessInfileUnits(
            "dMass", "1.0", str(folder), infile, sample_vplanet_help_dict
        )

        # Should contain "kg" (default mass unit)
        assert "kg" in units


class TestProcessOutputfile:
    """Tests for ProcessOutputfile function."""

    def test_process_output_file_basic(self, minimal_forward_file, minimal_vplanet_log):
        """
        Given: A forward evolution file and output order
        When: ProcessOutputfile is called
        Then: Data is correctly extracted into arrays
        """
        data = {}
        folder = minimal_forward_file.parent

        # First get the output order from log file
        log_data = {}
        process.ProcessLogFile(
            "earth.log", log_data, str(folder), verbose=False
        )

        output_order = {"earth:OutputOrder": log_data["earth:OutputOrder"]}

        result = process.ProcessOutputfile(
            "earth.earth.forward", data, "earth", output_order,
            ":forward", str(folder), verbose=False
        )

        # Check that forward data was extracted
        assert "earth:Time:forward" in result
        assert "earth:TMan:forward" in result

        # Check that data is in correct format [units, [array]]
        assert len(result["earth:Time:forward"]) == 2
        assert isinstance(result["earth:Time:forward"][1], list)

    def test_process_output_file_with_include_list(self, minimal_forward_file, minimal_vplanet_log):
        """
        Given: An output file and include list
        When: ProcessOutputfile is called with include list
        Then: Only included columns are extracted
        """
        data = {}
        folder = minimal_forward_file.parent

        log_data = {}
        process.ProcessLogFile(
            "earth.log", log_data, str(folder), verbose=False
        )

        output_order = {"earth:OutputOrder": log_data["earth:OutputOrder"]}
        include_list = ["earth:TMan:forward"]

        result = process.ProcessOutputfile(
            "earth.earth.forward", data, "earth", output_order,
            ":forward", str(folder), verbose=False, incl=include_list
        )

        # Only TMan should be extracted
        assert "earth:TMan:forward" in result
        assert "earth:Time:forward" not in result
        assert "earth:TCore:forward" not in result


class TestGatherData:
    """Tests for GatherData function."""

    def test_gather_data_complete(self, minimal_simulation_dir, sample_vplanet_help_dict):
        """
        Given: A complete simulation directory
        When: GatherData is called
        Then: All data types are gathered correctly
        """
        folder = str(minimal_simulation_dir)
        system_name = "earth"
        body_names = ["earth"]
        logfile = "earth.log"
        in_files = ["earth.in", "sun.in", "vpl.in"]

        data = {}
        result = process.GatherData(
            data, system_name, body_names, logfile, in_files,
            sample_vplanet_help_dict, folder, verbose=False
        )

        # Should have input file data
        assert any(":option" in key for key in result.keys())

        # Should have log file data
        assert any(":initial" in key for key in result.keys())
        assert any(":final" in key for key in result.keys())

        # Should have forward file data
        assert any(":forward" in key for key in result.keys())

    def test_gather_data_empty_initial(self, minimal_simulation_dir, sample_vplanet_help_dict):
        """
        Given: An empty data dictionary and simulation directory
        When: GatherData is called
        Then: Data is populated from scratch
        """
        folder = str(minimal_simulation_dir)
        system_name = "earth"
        body_names = ["earth"]
        logfile = "earth.log"
        in_files = ["earth.in", "vpl.in"]

        data = {}
        result = process.GatherData(
            data, system_name, body_names, logfile, in_files,
            sample_vplanet_help_dict, folder, verbose=False
        )

        assert isinstance(result, dict)
        assert len(result) > 0


class TestDictToBP:
    """Tests for DictToBP function."""

    def test_dict_to_bp_archive_mode(self, tempdir, sample_vplanet_help_dict):
        """
        Given: A data dictionary and HDF5 file
        When: DictToBP is called in archive mode
        Then: Data is written to specified group
        """
        data = {
            "earth:Mass:final": ["kg", "5.972e24"],
            "earth:Obliquity:final": ["rad", "0.408407"],
            "earth:TMan:forward": ["K", [3000, 2950, 2900]]
        }

        archive_file = tempdir / "test.bpa"
        with h5py.File(archive_file, "w") as hf:
            process.DictToBP(
                data, sample_vplanet_help_dict, hf,
                verbose=False, group_name="/sim_00", archive=True
            )

        # Verify data was written correctly
        with h5py.File(archive_file, "r") as hf:
            assert "/sim_00/earth:Mass:final" in hf
            assert hf["/sim_00/earth:Mass:final"].attrs["Units"] == "kg"

            assert "/sim_00/earth:Obliquity:final" in hf
            assert "/sim_00/earth:TMan:forward" in hf

    def test_dict_to_bp_filtered_mode(self, tempdir, sample_vplanet_help_dict):
        """
        Given: A data dictionary
        When: DictToBP is called in filtered mode
        Then: Data is written to root level
        """
        data = {
            "earth:Mass:final": ["kg", "5.972e24"],
            "earth:Obliquity:final": ["rad", "0.408407"]
        }

        filtered_file = tempdir / "test.bpf"
        with h5py.File(filtered_file, "w") as hf:
            process.DictToBP(
                data, sample_vplanet_help_dict, hf,
                verbose=False, group_name="", archive=False
            )

        # Verify data at root level
        with h5py.File(filtered_file, "r") as hf:
            assert "earth:Mass:final" in hf
            assert hf["earth:Mass:final"].attrs["Units"] == "kg"

    def test_dict_to_bp_output_order(self, tempdir, sample_vplanet_help_dict):
        """
        Given: Data with OutputOrder
        When: DictToBP is called
        Then: OutputOrder is written as string array
        """
        data = {
            "earth:OutputOrder": [["Time", "sec"], ["TMan", "K"]]
        }

        test_file = tempdir / "test.bpf"
        with h5py.File(test_file, "w") as hf:
            process.DictToBP(
                data, sample_vplanet_help_dict, hf,
                verbose=False, group_name="", archive=False
            )

        with h5py.File(test_file, "r") as hf:
            assert "earth:OutputOrder" in hf
            # Should be stored as string type
            dataset = hf["earth:OutputOrder"]
            assert dataset.dtype.kind in ['S', 'O', 'U']  # String types


class TestProcessSeasonalClimatefile:
    """Tests for ProcessSeasonalClimatefile function."""

    def test_process_seasonal_climate_file(self, tempdir):
        """
        Given: A seasonal climate file
        When: ProcessSeasonalClimatefile is called
        Then: Data is correctly extracted with proper units
        """
        # Create sample climate data file
        climate_dir = tempdir / "SeasonalClimateFiles"
        climate_dir.mkdir()

        data_array = np.random.rand(10, 10)  # Sample climate grid
        climate_file = climate_dir / "earth.DailyInsol.0"
        np.savetxt(climate_file, data_array)

        data = {}
        result = process.ProcessSeasonalClimatefile(
            "earth", data, "earth", "DailyInsol",
            str(tempdir), verbose=False
        )

        # Check that data was extracted
        assert "earth:DailyInsol" in result
        assert len(result["earth:DailyInsol"]) == 2
        assert result["earth:DailyInsol"][0] == "W/m^2"  # Correct units for DailyInsol

    def test_process_seasonal_climate_temperature(self, tempdir):
        """
        Given: A seasonal temperature file
        When: ProcessSeasonalClimatefile is called
        Then: Correct units are assigned
        """
        climate_dir = tempdir / "SeasonalClimateFiles"
        climate_dir.mkdir()

        data_array = np.random.rand(10, 10)
        climate_file = climate_dir / "earth.SeasonalTemp.0"
        np.savetxt(climate_file, data_array)

        data = {}
        result = process.ProcessSeasonalClimatefile(
            "earth", data, "earth", "SeasonalTemp",
            str(tempdir), verbose=False
        )

        assert result["earth:SeasonalTemp"][0] == "deg C"


# Integration test for full processing pipeline
class TestProcessingPipeline:
    """Integration tests for complete data processing workflow."""

    def test_full_processing_pipeline(self, minimal_simulation_dir, sample_vplanet_help_dict):
        """
        Given: A complete simulation directory
        When: Full processing pipeline is executed
        Then: All data is correctly gathered and can be written to HDF5
        """
        folder = str(minimal_simulation_dir)
        system_name = "earth"
        body_names = ["earth"]
        logfile = "earth.log"
        in_files = ["earth.in", "vpl.in"]

        # Gather data
        data = process.GatherData(
            {}, system_name, body_names, logfile, in_files,
            sample_vplanet_help_dict, folder, verbose=False
        )

        # Write to HDF5
        test_file = minimal_simulation_dir.parent / "test.bpa"
        with h5py.File(test_file, "w") as hf:
            process.DictToBP(
                data, sample_vplanet_help_dict, hf,
                verbose=False, group_name="/sim_00", archive=True
            )

        # Verify file was created and contains data
        assert test_file.exists()
        with h5py.File(test_file, "r") as hf:
            assert "/sim_00" in hf
            assert len(list(hf["/sim_00"].keys())) > 0
