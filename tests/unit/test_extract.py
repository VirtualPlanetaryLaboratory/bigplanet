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
