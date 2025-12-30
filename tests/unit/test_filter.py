"""
Unit tests for filter module.

Tests the BigPlanet filter functionality, including key categorization
and filter file creation.
"""

import os
import pathlib
import pytest
import h5py
import numpy as np

from bigplanet import filter


class TestSplitsaKey:
    """Tests for SplitsaKey() function."""

    def test_split_key_log_initial(self):
        """
        Given: Key list with initial values
        When: SplitsaKey is called
        Then: Returns keys in loglist
        """
        saKeylist = ["earth:Mass:initial", "star:Luminosity:initial"]

        loglist, bodylist, forwardlist, climatelist, backwardlist = filter.SplitsaKey(
            saKeylist, verbose=False
        )

        assert len(loglist) == 2
        assert "earth:Mass:initial" in loglist
        assert "star:Luminosity:initial" in loglist
        assert len(bodylist) == 0
        assert len(forwardlist) == 0

    def test_split_key_log_final(self):
        """
        Given: Key list with final values
        When: SplitsaKey is called
        Then: Returns keys in loglist
        """
        saKeylist = ["earth:Eccentricity:final", "earth:SemiMajorAxis:final"]

        loglist, bodylist, forwardlist, climatelist, backwardlist = filter.SplitsaKey(
            saKeylist, verbose=False
        )

        assert len(loglist) == 2
        assert "earth:Eccentricity:final" in loglist
        assert len(forwardlist) == 0

    def test_split_key_forward(self):
        """
        Given: Key list with forward evolution keys
        When: SplitsaKey is called
        Then: Returns keys in forwardlist
        """
        saKeylist = ["earth:Temperature:forward", "earth:SurfaceWaterMass:forward"]

        loglist, bodylist, forwardlist, climatelist, backwardlist = filter.SplitsaKey(
            saKeylist, verbose=False
        )

        assert len(forwardlist) == 2
        assert "earth:Temperature:forward" in forwardlist
        assert "earth:SurfaceWaterMass:forward" in forwardlist
        assert len(loglist) == 0

    def test_split_key_backward(self):
        """
        Given: Key list with backward evolution keys
        When: SplitsaKey is called
        Then: Returns keys in backwardlist
        """
        saKeylist = ["earth:Eccentricity:backward"]

        loglist, bodylist, forwardlist, climatelist, backwardlist = filter.SplitsaKey(
            saKeylist, verbose=False
        )

        assert len(backwardlist) == 1
        assert "earth:Eccentricity:backward" in backwardlist

    def test_split_key_climate(self):
        """
        Given: Key list with climate data keys
        When: SplitsaKey is called
        Then: Returns keys in climatelist
        """
        saKeylist = ["earth:TempLandDaily:climate", "earth:AlbedoLand:climate"]

        loglist, bodylist, forwardlist, climatelist, backwardlist = filter.SplitsaKey(
            saKeylist, verbose=False
        )

        assert len(climatelist) == 2
        assert "earth:TempLandDaily:climate" in climatelist

    def test_split_key_option(self):
        """
        Given: Key list with option/input file keys
        When: SplitsaKey is called
        Then: Returns keys in bodylist
        """
        saKeylist = ["earth:dMass:option", "star:dAge:option"]

        loglist, bodylist, forwardlist, climatelist, backwardlist = filter.SplitsaKey(
            saKeylist, verbose=False
        )

        assert len(bodylist) == 2
        assert "earth:dMass:option" in bodylist
        assert "star:dAge:option" in bodylist

    def test_split_key_stats_mean(self):
        """
        Given: Key list with statistical mean keys
        When: SplitsaKey is called
        Then: Returns keys in forwardlist (stats treated as forward)
        """
        saKeylist = ["earth:Eccentricity:mean", "earth:SemiMajorAxis:stddev"]

        loglist, bodylist, forwardlist, climatelist, backwardlist = filter.SplitsaKey(
            saKeylist, verbose=False
        )

        assert len(forwardlist) == 2
        assert "earth:Eccentricity:mean" in forwardlist
        assert "earth:SemiMajorAxis:stddev" in forwardlist

    def test_split_key_stats_all_types(self):
        """
        Given: Key list with all statistical function types
        When: SplitsaKey is called
        Then: All stats keys go to forwardlist
        """
        saKeylist = [
            "earth:Temperature:mean",
            "earth:Temperature:mode",
            "earth:Temperature:max",
            "earth:Temperature:min",
            "earth:Temperature:geomean",
            "earth:Temperature:stddev",
        ]

        loglist, bodylist, forwardlist, climatelist, backwardlist = filter.SplitsaKey(
            saKeylist, verbose=False
        )

        assert len(forwardlist) == 6

    def test_split_key_mixed_list(self):
        """
        Given: Key list with multiple key types
        When: SplitsaKey is called
        Then: Correctly categorizes each key type
        """
        saKeylist = [
            "earth:Mass:initial",
            "earth:Eccentricity:final",
            "earth:dMass:option",
            "earth:Temperature:forward",
            "earth:TempLand:climate",
            "earth:Obliquity:backward",
        ]

        loglist, bodylist, forwardlist, climatelist, backwardlist = filter.SplitsaKey(
            saKeylist, verbose=False
        )

        assert len(loglist) == 2
        assert len(bodylist) == 1
        assert len(forwardlist) == 1
        assert len(climatelist) == 1
        assert len(backwardlist) == 1

    def test_split_key_verbose_mode(self, capsys):
        """
        Given: Key list with verbose=True
        When: SplitsaKey is called
        Then: Prints categorized lists
        """
        saKeylist = ["earth:Mass:initial", "earth:dMass:option"]

        loglist, bodylist, forwardlist, climatelist, backwardlist = filter.SplitsaKey(
            saKeylist, verbose=True
        )

        captured = capsys.readouterr()
        assert "Log file:" in captured.out
        assert "Body file:" in captured.out
        assert "Forward File:" in captured.out

    def test_split_key_output_order(self):
        """
        Given: Key list with OutputOrder keys
        When: SplitsaKey is called
        Then: Returns keys in loglist
        """
        saKeylist = ["earth:OutputOrder:OutputOption", "star:GridOutputOrder:GridOutputOption"]

        loglist, bodylist, forwardlist, climatelist, backwardlist = filter.SplitsaKey(
            saKeylist, verbose=False
        )

        assert len(loglist) == 2
        assert "earth:OutputOrder:OutputOption" in loglist
        assert "star:GridOutputOrder:GridOutputOption" in loglist

    def test_split_key_empty_list(self):
        """
        Given: Empty key list
        When: SplitsaKey is called
        Then: Returns all empty lists
        """
        saKeylist = []

        loglist, bodylist, forwardlist, climatelist, backwardlist = filter.SplitsaKey(
            saKeylist, verbose=False
        )

        assert len(loglist) == 0
        assert len(bodylist) == 0
        assert len(forwardlist) == 0
        assert len(climatelist) == 0
        assert len(backwardlist) == 0


# TODO: Add integration tests for Filter() function
# These require more complex setup with proper BPL input files, simulation directories,
# and archive files. The SplitsaKey function is well-tested above, and Filter()'s
# archive extraction path is covered by existing integration tests in tests/ExtractFilter*.
