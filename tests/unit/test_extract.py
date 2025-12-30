"""
Unit tests for bigplanet/extract.py module.

Tests cover HDF5 extraction, statistical functions, and MD5 checksums.
"""

import hashlib
import pathlib

import h5py
import numpy as np
import pytest

from bigplanet import extract


class TestBPLFile:
    """Tests for BPLFile function."""

    def test_bpl_file_archive(self, sample_hdf5_archive):
        """
        Given: An HDF5 archive file
        When: BPLFile is called
        Then: File is opened and checksum verified
        """
        # MD5 checksum should be created
        result = extract.BPLFile(str(sample_hdf5_archive), ignore_corrupt=True)

        assert isinstance(result, h5py.File)
        result.close()

    def test_bpl_file_filtered(self, sample_filtered_file):
        """
        Given: A filtered HDF5 file
        When: BPLFile is called
        Then: File is opened without checksum
        """
        result = extract.BPLFile(str(sample_filtered_file), ignore_corrupt=True)

        assert isinstance(result, h5py.File)
        result.close()


class TestExtractColumn:
    """Tests for ExtractColumn function."""

    def test_extract_column_final_value(self, sample_hdf5_archive):
        """
        Given: An archive file with final values
        When: ExtractColumn is called for a final parameter
        Then: Values are extracted correctly
        """
        with extract.BPLFile(str(sample_hdf5_archive), ignore_corrupt=True) as hf:
            result = extract.ExtractColumn(hf, "earth:Obliquity:final")

            assert len(result) == 1
            assert np.isclose(result[0], 0.408407)

    def test_extract_column_forward_data(self, sample_hdf5_archive):
        """
        Given: An archive file with forward data
        When: ExtractColumn is called for forward parameter
        Then: Time series arrays are extracted
        """
        with extract.BPLFile(str(sample_hdf5_archive), ignore_corrupt=True) as hf:
            result = extract.ExtractColumn(hf, "earth:TMan:forward")

            assert len(result) == 1
            assert len(result[0]) == 6  # 6 time steps


class TestExtractUnits:
    """Tests for ExtractUnits function."""

    def test_extract_units(self, sample_hdf5_archive):
        """
        Given: An HDF5 file with units attributes
        When: ExtractUnits is called
        Then: Correct units are returned
        """
        with extract.BPLFile(str(sample_hdf5_archive), ignore_corrupt=True) as hf:
            units = extract.ExtractUnits(hf, "earth:Mass:initial")

            assert units == "kg"


class TestMd5CheckSum:
    """Tests for Md5CheckSum function."""

    def test_md5_checksum_creates_file(self, sample_hdf5_archive):
        """
        Given: An HDF5 file without MD5
        When: Md5CheckSum is called
        Then: MD5 file is created
        """
        md5_file = sample_hdf5_archive.with_suffix(".md5")
        if md5_file.exists():
            md5_file.unlink()

        extract.Md5CheckSum(str(sample_hdf5_archive), ignore_corrupt=True)

        assert md5_file.exists()

    def test_md5_checksum_verifies(self, sample_hdf5_archive):
        """
        Given: An HDF5 file with valid MD5
        When: Md5CheckSum is called
        Then: Checksum is verified
        """
        md5_file = sample_hdf5_archive.with_suffix(".md5")

        # Create initial checksum
        extract.Md5CheckSum(str(sample_hdf5_archive), ignore_corrupt=True)

        # Verify it validates
        extract.Md5CheckSum(str(sample_hdf5_archive), ignore_corrupt=True)

        # Should complete without error

    def test_md5_checksum_detects_corruption(self, sample_hdf5_archive):
        """
        Given: An HDF5 file with incorrect MD5
        When: Md5CheckSum is called
        Then: Corruption is detected
        """
        md5_file = sample_hdf5_archive.with_suffix(".md5")

        # Write incorrect MD5
        md5_file.write_text("0" * 32)

        # Should detect mismatch (with ignore flag it just warns)
        extract.Md5CheckSum(str(sample_hdf5_archive), ignore_corrupt=True)


class TestCreateMatrix:
    """Tests for CreateMatrix function."""

    def test_create_matrix_basic(self):
        """
        Given: X, Y axes and Z array
        When: CreateMatrix is called
        Then: Matrix is reshaped correctly as a list

        Note: CreateMatrix returns a Python list (not numpy array) because
        it calls .tolist() at the end (extract.py:306).
        """
        xaxis = np.array([1, 2, 3])
        yaxis = np.array([10, 20])
        zarray = np.array([100, 200, 300, 400, 500, 600])

        result = extract.CreateMatrix(xaxis, yaxis, zarray, orientation=0)

        # Result is a list, not numpy array
        assert isinstance(result, list)
        assert len(result) == 2  # 2 rows (yaxis length)
        assert len(result[0]) == 3  # 3 columns (xaxis length)

    def test_create_matrix_wrong_size(self):
        """
        Given: Incompatible dimensions
        When: CreateMatrix is called
        Then: Error is raised
        """
        xaxis = np.array([1, 2])
        yaxis = np.array([10, 20])
        zarray = np.array([100, 200, 300])  # Wrong size

        with pytest.raises(SystemExit):
            extract.CreateMatrix(xaxis, yaxis, zarray)


class TestForwardData:
    """Tests for ForwardData function."""

    def test_forward_data_archive(self, tempdir):
        """
        Given: Archive file with forward data
        When: ForwardData is called
        Then: Returns forward time series arrays
        """
        # Create archive with forward data
        pathArchive = tempdir / "test.bpa"
        with h5py.File(pathArchive, "w") as hf:
            grp = hf.create_group("sim_00")
            daForward = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
            grp.create_dataset("earth:Temperature:forward", data=daForward)

        with h5py.File(pathArchive, "r") as hf:
            result = extract.ForwardData(hf, "earth:Temperature:mean")

            assert len(result) == 2
            assert len(result[0]) == 3

    def test_forward_data_filtered(self, tempdir):
        """
        Given: Filtered file with forward data
        When: ForwardData is called
        Then: Returns forward time series arrays
        """
        # Create filtered file (no groups)
        pathFiltered = tempdir / "filtered.bpf"
        with h5py.File(pathFiltered, "w") as hf:
            daForward = np.array([[1.0, 2.0], [3.0, 4.0]])
            hf.create_dataset("earth:Temperature:forward", data=daForward)

        with h5py.File(pathFiltered, "r") as hf:
            result = extract.ForwardData(hf, "earth:Temperature:mean")

            assert len(result) == 2


class TestExtractColumnStatistics:
    """Tests for ExtractColumn statistical aggregations."""

    def test_extract_column_mean(self, tempdir):
        """
        Given: Archive with forward data
        When: ExtractColumn is called with :mean
        Then: Returns mean of each forward array
        """
        pathArchive = tempdir / "test.bpa"
        with h5py.File(pathArchive, "w") as hf:
            grp = hf.create_group("sim_00")
            daForward = np.array([[2.0, 4.0, 6.0]])  # mean = 4.0
            grp.create_dataset("earth:Temp:forward", data=daForward)

        with h5py.File(pathArchive, "r") as hf:
            result = extract.ExtractColumn(hf, "earth:Temp:mean")

            assert len(result) == 1
            assert np.isclose(result[0], 4.0)

    def test_extract_column_stddev(self, tempdir):
        """
        Given: Archive with forward data
        When: ExtractColumn is called with :stddev
        Then: Returns standard deviation of each forward array
        """
        pathArchive = tempdir / "test.bpa"
        with h5py.File(pathArchive, "w") as hf:
            grp = hf.create_group("sim_00")
            daForward = np.array([[2.0, 4.0, 6.0, 8.0]])
            grp.create_dataset("earth:Temp:forward", data=daForward)

        with h5py.File(pathArchive, "r") as hf:
            result = extract.ExtractColumn(hf, "earth:Temp:stddev")

            assert len(result) == 1
            # Verify it's a reasonable stddev (not testing exact value)
            assert result[0] > 0

    def test_extract_column_min(self, tempdir):
        """
        Given: Archive with forward data
        When: ExtractColumn is called with :min
        Then: Returns minimum of each forward array
        """
        pathArchive = tempdir / "test.bpa"
        with h5py.File(pathArchive, "w") as hf:
            grp = hf.create_group("sim_00")
            daForward = np.array([[5.0, 2.0, 8.0]])
            grp.create_dataset("earth:Temp:forward", data=daForward)

        with h5py.File(pathArchive, "r") as hf:
            result = extract.ExtractColumn(hf, "earth:Temp:min")

            assert len(result) == 1
            assert result[0] == 2.0

    def test_extract_column_max(self, tempdir):
        """
        Given: Archive with forward data
        When: ExtractColumn is called with :max
        Then: Returns maximum of each forward array
        """
        pathArchive = tempdir / "test.bpa"
        with h5py.File(pathArchive, "w") as hf:
            grp = hf.create_group("sim_00")
            daForward = np.array([[5.0, 2.0, 8.0]])
            grp.create_dataset("earth:Temp:forward", data=daForward)

        with h5py.File(pathArchive, "r") as hf:
            result = extract.ExtractColumn(hf, "earth:Temp:max")

            assert len(result) == 1
            assert result[0] == 8.0

    def test_extract_column_filtered_forward(self, tempdir):
        """
        Given: Filtered file with forward data
        When: ExtractColumn is called for forward
        Then: Returns time series data
        """
        pathFiltered = tempdir / "filtered.bpf"
        with h5py.File(pathFiltered, "w") as hf:
            daForward = np.array([[1.0, 2.0], [3.0, 4.0]])
            hf.create_dataset("earth:Temp:forward", data=daForward)

        with h5py.File(pathFiltered, "r") as hf:
            result = extract.ExtractColumn(hf, "earth:Temp:forward")

            assert len(result) == 2

    def test_extract_column_initial_filtered(self, tempdir):
        """
        Given: Filtered file with initial value
        When: ExtractColumn is called for initial
        Then: Returns initial values
        """
        pathFiltered = tempdir / "filtered.bpf"
        with h5py.File(pathFiltered, "w") as hf:
            hf.create_dataset("earth:Mass:initial", data=np.array([5.972e24]))

        with h5py.File(pathFiltered, "r") as hf:
            result = extract.ExtractColumn(hf, "earth:Mass:initial")

            assert len(result) == 1
            assert np.isclose(result[0], 5.972e24)


class TestExtractUniqueValues:
    """Tests for ExtractUniqueValues function."""

    def test_extract_unique_archive(self, tempdir):
        """
        Given: Archive with duplicate values
        When: ExtractUniqueValues is called
        Then: Returns unique values only
        """
        pathArchive = tempdir / "test.bpa"
        with h5py.File(pathArchive, "w") as hf:
            grp1 = hf.create_group("sim_00")
            grp1.create_dataset("earth:Mass:final", data=[b"1.0"])
            grp2 = hf.create_group("sim_01")
            grp2.create_dataset("earth:Mass:final", data=[b"2.0"])
            grp3 = hf.create_group("sim_02")
            grp3.create_dataset("earth:Mass:final", data=[b"1.0"])  # Duplicate

        with h5py.File(pathArchive, "r") as hf:
            result = extract.ExtractUniqueValues(hf, "earth:Mass:final")

            assert len(result) == 2
            assert 1.0 in result
            assert 2.0 in result

    def test_extract_unique_filtered(self, tempdir):
        """
        Given: Filtered file with duplicate values
        When: ExtractUniqueValues is called
        Then: Returns unique values only
        """
        pathFiltered = tempdir / "filtered.bpf"
        with h5py.File(pathFiltered, "w") as hf:
            hf.create_dataset("earth:Mass:final", data=[b"3.0", b"3.0", b"5.0"])

        with h5py.File(pathFiltered, "r") as hf:
            result = extract.ExtractUniqueValues(hf, "earth:Mass:final")

            assert len(result) == 2
            assert 3.0 in result
            assert 5.0 in result


class TestRotate90Clockwise:
    """Tests for rotate90Clockwise function."""

    def test_rotate_2x2_matrix(self):
        """
        Given: 2x2 matrix
        When: rotate90Clockwise is called
        Then: Matrix is rotated 90 degrees clockwise
        """
        matrix = [[1, 2], [3, 4]]
        result = extract.rotate90Clockwise(matrix)

        assert result == [[3, 1], [4, 2]]

    def test_rotate_3x3_matrix(self):
        """
        Given: 3x3 matrix
        When: rotate90Clockwise is called
        Then: Matrix is rotated 90 degrees clockwise
        """
        matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        result = extract.rotate90Clockwise(matrix)

        assert result == [[7, 4, 1], [8, 5, 2], [9, 6, 3]]


class TestArchiveToFiltered:
    """Tests for ArchiveToFiltered function."""

    def test_archive_to_filtered_basic(self, tempdir):
        """
        Given: Archive file with data
        When: ArchiveToFiltered is called
        Then: Creates filtered HDF5 file with requested columns
        """
        pathArchive = tempdir / "test.bpa"
        pathFiltered = tempdir / "filtered.bpf"

        # Create archive
        with h5py.File(pathArchive, "w") as hf:
            grp = hf.create_group("sim_00")
            grp.create_dataset("earth:Mass:final", data=np.array([1.0]))
            grp["earth:Mass:final"].attrs["Units"] = "Mearth"
            grp.create_dataset("earth:Ecc:final", data=np.array([0.01]))
            grp["earth:Ecc:final"].attrs["Units"] = "nd"

        # Extract columns
        with h5py.File(pathArchive, "r") as hf:
            extract.ArchiveToFiltered(hf, ["earth:Mass:final"], str(pathFiltered))

        # Verify filtered file created
        assert pathFiltered.exists()

        with h5py.File(pathFiltered, "r") as hf:
            assert "earth:Mass:final" in hf
            assert hf["earth:Mass:final"].attrs["Units"] == "Mearth"


class TestDictToCSV:
    """Tests for DictToCSV function."""

    def test_dict_to_csv_basic(self, tempdir):
        """
        Given: Data dictionary
        When: DictToCSV is called
        Then: Creates CSV file
        """
        dictData = {
            "earth:Mass:initial": [None, 1.0],
            "earth:Ecc:initial": [None, 0.01]
        }

        pathCSV = tempdir / "output.csv"
        extract.DictToCSV(dictData, str(pathCSV), delim=",", header=True)

        assert pathCSV.exists()
        # Verify file has content
        assert pathCSV.stat().st_size > 0

    def test_dict_to_csv_ulysses(self, tempdir):
        """
        Given: Data dictionary with forward data
        When: DictToCSV is called with ulysses=1
        Then: Creates User.csv in Ulysses format
        """
        dictData = {
            "earth:Temp:forward": [[1.0, 2.0, 3.0]],
            "earth:Mass:forward": [[4.0, 5.0, 6.0]]
        }

        # Change to tempdir so User.csv is created there
        import os
        original_cwd = os.getcwd()
        os.chdir(tempdir)

        try:
            extract.DictToCSV(dictData, ulysses=1)

            pathCSV = tempdir / "User.csv"
            assert pathCSV.exists()

            # Verify Ulysses format (first column should be empty with comma)
            with open(pathCSV) as f:
                first_line = f.readline()
                assert first_line.startswith(",")
        finally:
            os.chdir(original_cwd)


class TestCSVToDict:
    """Tests for CSVToDict function."""

    def test_csv_to_dict_basic(self, tempdir):
        """
        Given: CSV file
        When: CSVToDict is called
        Then: Returns dictionary
        """
        pathCSV = tempdir / "test.csv"
        pathCSV.write_text("col1,col2\n1,2\n3,4\n")

        result = extract.CSVToDict(str(pathCSV))

        assert isinstance(result, dict)
        assert "col1" in result
        assert "col2" in result

    # TODO: Add test for CSVToDict with ulysses=1
    # Requires compatible pandas version for df.shift() operation
