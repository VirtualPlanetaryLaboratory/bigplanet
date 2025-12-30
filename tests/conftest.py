"""
Pytest configuration and shared fixtures for BigPlanet tests.

This module provides reusable test fixtures and utilities for both unit
and integration tests.
"""

import os
import pathlib
import shutil
import tempfile
from typing import Dict, List

import h5py
import numpy as np
import pytest


@pytest.fixture
def tempdir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield pathlib.Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def minimal_vplanet_log(tempdir):
    """Create a minimal VPLanet log file for testing."""
    log_content = """-------- Log file earth.log -------

Executable: /usr/local/bin/vplanet
Version: 1.0.0
System Name: earth
Primary Input File: vpl.in
Body File #1: sun.in
Body File #2: earth.in

---- INITIAL SYSTEM PROPERTIES ----
(Age) System Age [sec]: 0.000000
(Time) Simulation Time [sec]: 0.000000
(TotAngMom) Total Angular Momentum [kg*m^2/sec]: 1.474456e+42

----- BODY: sun ----
Active Modules: STELLAR
(Mass) Mass [kg]: 1.988416e+30
(Radius) Radius [m]: 2.019571e+08
(RotPer) Rotational Period [sec]: 8.640000e+04
(Luminosity) Luminosity [kg*m^2/sec^3]: 3.846000e+26
Output Order: Time [sec] Luminosity [kg*m^2/sec^3] Radius [m]
Grid Output Order:

----- BODY: earth ----
Active Modules: RadHeat ThermInt
(Mass) Mass [kg]: 5.972e+24
(Radius) Radius [m]: 6.371e+06
(Obliquity) Obliquity [rad]: 0.408407
(Eccentricity) Orbital Eccentricity []: 0.0167
Output Order: Time [sec] TMan [K] TCore [K] Eccentricity [] Obliquity [rad]
Grid Output Order:

---- FINAL SYSTEM PROPERTIES ----
(Age) System Age [sec]: 1.577880e+17
(Time) Simulation Time [sec]: 1.577880e+17
(TotAngMom) Total Angular Momentum [kg*m^2/sec]: 1.474456e+42

----- BODY: sun ----
(Mass) Mass [kg]: 1.988416e+30
(Radius) Radius [m]: 2.050000e+08
(RotPer) Rotational Period [sec]: 8.640000e+04
(Luminosity) Luminosity [kg*m^2/sec^3]: 3.950000e+26

----- BODY: earth ----
(Mass) Mass [kg]: 5.972e+24
(Radius) Radius [m]: 6.371e+06
(Obliquity) Obliquity [rad]: 0.408407
(Eccentricity) Orbital Eccentricity []: 0.0167
"""
    log_file = tempdir / "earth.log"
    log_file.write_text(log_content)
    return log_file


@pytest.fixture
def minimal_vplanet_input(tempdir, minimal_vpl_input):
    """Create a minimal VPLanet input file for testing.

    Also creates vpl.in since ProcessInputfile depends on it.
    """
    input_content = """# Earthlike parameters
sName		earth
saModules 	radheat thermint

# Physical Properties
dMass		-1.0
dRadius		-1.0
dRotPeriod	-1.0
dObliquity	23.5
dRadGyra	0.5

# Orbital Properties
dEcc            0.0167
dSemi           1.0

# THERMINT inputs
dTMan          3000
dTCore         6000

saOutputOrder -Time -TMan -TCore -Eccentricity -Obliquity
"""
    input_file = tempdir / "earth.in"
    input_file.write_text(input_content)
    return input_file


@pytest.fixture
def minimal_vpl_input(tempdir):
    """Create a minimal vpl.in (primary file) for testing."""
    vpl_content = """# Primary input file
sSystemName	earth
sPrimaryFile	vpl.in
saBodyFiles	earth.in sun.in

sUnitMass	kg
sUnitLength	m
sUnitTime	sec
sUnitAngle	rad

dStopTime	5e9
dOutputTime	1e8

bOverwrite	1
"""
    vpl_file = tempdir / "vpl.in"
    vpl_file.write_text(vpl_content)
    return vpl_file


@pytest.fixture
def minimal_forward_file(tempdir):
    """Create a minimal forward evolution file for testing."""
    # Create sample time series data
    times = np.array([0, 1e9, 2e9, 3e9, 4e9, 5e9])
    tman = np.array([3000, 2950, 2900, 2850, 2800, 2750])
    tcore = np.array([6000, 5900, 5800, 5700, 5600, 5500])
    ecc = np.array([0.0167, 0.0165, 0.0163, 0.0161, 0.0160, 0.0158])
    obl = np.array([0.4084, 0.4080, 0.4075, 0.4070, 0.4065, 0.4060])

    data = np.column_stack([times, tman, tcore, ecc, obl])

    forward_file = tempdir / "earth.earth.forward"
    np.savetxt(forward_file, data, fmt='%.6e')
    return forward_file


@pytest.fixture
def minimal_bpl_input(tempdir):
    """Create a minimal BigPlanet input file for testing."""
    bpl_content = """sDestFolder test_sims

saBodyFiles  earth.in sun.in
sPrimaryFile vpl.in
"""
    bpl_file = tempdir / "bpl.in"
    bpl_file.write_text(bpl_content)
    return bpl_file


@pytest.fixture
def minimal_simulation_dir(tempdir, minimal_vpl_input, minimal_vplanet_input,
                          minimal_vplanet_log, minimal_forward_file):
    """Create a minimal simulation directory structure."""
    sim_dir = tempdir / "test_sims" / "sim_00"
    sim_dir.mkdir(parents=True)

    # Copy files to simulation directory
    shutil.copy(minimal_vpl_input, sim_dir / "vpl.in")
    shutil.copy(minimal_vplanet_input, sim_dir / "earth.in")
    shutil.copy(minimal_vplanet_log, sim_dir / "earth.log")
    shutil.copy(minimal_forward_file, sim_dir / "earth.earth.forward")

    # Create a minimal sun.in
    sun_content = """sName		sun
saModules 	stellar

dMass		1.0
dAge		1e6
"""
    (sim_dir / "sun.in").write_text(sun_content)

    return sim_dir


@pytest.fixture
def sample_vplanet_help_dict():
    """Return a sample VPLanet help dictionary for testing."""
    return {
        "dMass": {
            "Type": "Double",
            "Dimension": "mass",
            "Default Value": "0.0"
        },
        "dRadius": {
            "Type": "Double",
            "Dimension": "length",
            "Default Value": "0.0"
        },
        "dSemi": {
            "Type": "Double",
            "Dimension": "length",
            "Default Value": "0.0",
            "Custom Units": "AU"
        },
        "dObliquity": {
            "Type": "Double",
            "Dimension": "angle",
            "Default Value": "0.0"
        },
        "dTMan": {
            "Type": "Double",
            "Dimension": "temperature",
            "Default Value": "3000.0"
        },
        "sName": {
            "Type": "String",
            "Dimension": "nd",
            "Default Value": ""
        },
        "saOutputOrder": {
            "Type": "String-Array",
            "Dimension": "nd",
            "Default Value": ""
        },
        "sUnitMass": {
            "Default Value": "kg"
        },
        "sUnitLength": {
            "Default Value": "m"
        },
        "sUnitTime": {
            "Default Value": "sec"
        },
        "sUnitAngle": {
            "Default Value": "rad"
        },
        "sUnitTemp": {
            "Default Value": "K"
        }
    }


@pytest.fixture
def sample_hdf5_archive(tempdir):
    """Create a sample HDF5 archive file for testing."""
    archive_file = tempdir / "test.bpa"

    with h5py.File(archive_file, "w") as f:
        # Create a sample simulation group
        grp = f.create_group("sim_00")

        # Add some sample data
        grp.create_dataset("earth:Mass:initial", data=[5.972e24])
        grp["earth:Mass:initial"].attrs["Units"] = "kg"

        grp.create_dataset("earth:Obliquity:final", data=[0.408407])
        grp["earth:Obliquity:final"].attrs["Units"] = "rad"

        grp.create_dataset("earth:TMan:forward",
                          data=[[3000, 2950, 2900, 2850, 2800, 2750]])
        grp["earth:TMan:forward"].attrs["Units"] = "K"

        # Add OutputOrder
        output_order = [["Time", "sec"], ["TMan", "K"], ["TCore", "K"]]
        grp.create_dataset("earth:OutputOrder",
                          data=np.array(output_order, dtype='S'))
        grp["earth:OutputOrder"].attrs["Units"] = ""

    return archive_file


@pytest.fixture
def sample_filtered_file(tempdir):
    """Create a sample filtered HDF5 file for testing."""
    filtered_file = tempdir / "test.bpf"

    with h5py.File(filtered_file, "w") as f:
        # Filtered files have data at root level, not in groups
        f.create_dataset("earth:Mass:initial", data=[5.972e24, 5.972e24])
        f["earth:Mass:initial"].attrs["Units"] = "kg"

        f.create_dataset("earth:Obliquity:final", data=[0.408407, 0.410000])
        f["earth:Obliquity:final"].attrs["Units"] = "rad"

    return filtered_file


def flistStripComments(listLines: List[str]) -> List[str]:
    """
    Remove comments and blank lines from a list of file lines.

    Parameters
    ----------
    listLines : list of str
        Lines from an input file

    Returns
    -------
    list of str
        Lines with comments and blanks removed
    """
    listCleaned = []
    for sLine in listLines:
        sLine = sLine.strip()
        if not sLine or sLine.startswith("#"):
            continue
        # Remove inline comments
        if "#" in sLine:
            sLine = sLine.partition("#")[0].strip()
        if sLine:
            listCleaned.append(sLine)
    return listCleaned


def fbFloatsClose(fVal1: float, fVal2: float, fTolerance: float = 1e-6) -> bool:
    """
    Check if two floating point values are close within tolerance.

    Parameters
    ----------
    fVal1 : float
        First value
    fVal2 : float
        Second value
    fTolerance : float, optional
        Relative tolerance (default 1e-6)

    Returns
    -------
    bool
        True if values are close within tolerance
    """
    return np.isclose(fVal1, fVal2, rtol=fTolerance)


def fbArraysClose(daArray1: np.ndarray, daArray2: np.ndarray,
                 fTolerance: float = 1e-6) -> bool:
    """
    Check if two numpy arrays are close within tolerance.

    Parameters
    ----------
    daArray1 : np.ndarray
        First array
    daArray2 : np.ndarray
        Second array
    fTolerance : float, optional
        Relative tolerance (default 1e-6)

    Returns
    -------
    bool
        True if all elements are close within tolerance
    """
    return np.allclose(daArray1, daArray2, rtol=fTolerance)


# Checkpoint file fixtures for testing bpstatus and archive functionality

@pytest.fixture
def checkpoint_file_all_done(tempdir):
    """
    Create a checkpoint file with all simulations complete (status=1).

    Returns
    -------
    pathlib.Path
        Path to checkpoint file
    """
    pathCheckpoint = tempdir / ".test_sims_BPL"
    with open(pathCheckpoint, "w") as f:
        f.write(f"Vspace File: {tempdir}/bpl.in\n")
        f.write("Total Number of Simulations: 3\n")
        f.write("sim_00 1\n")
        f.write("sim_01 1\n")
        f.write("sim_02 1\n")
        f.write("THE END\n")
    return pathCheckpoint


@pytest.fixture
def checkpoint_file_in_progress(tempdir):
    """
    Create a checkpoint file with mixed statuses (-1, 0, 1).

    Status breakdown: 2 done, 1 in-progress, 2 remaining

    Returns
    -------
    pathlib.Path
        Path to checkpoint file
    """
    pathCheckpoint = tempdir / ".test_sims_BPL"
    with open(pathCheckpoint, "w") as f:
        f.write(f"Vspace File: {tempdir}/bpl.in\n")
        f.write("Total Number of Simulations: 5\n")
        f.write("sim_00 1\n")   # Done
        f.write("sim_01 0\n")   # In progress
        f.write("sim_02 -1\n")  # To do
        f.write("sim_03 1\n")   # Done
        f.write("sim_04 -1\n")  # To do
        f.write("THE END\n")
    return pathCheckpoint


@pytest.fixture
def checkpoint_file_none_started(tempdir):
    """
    Create a checkpoint file with all simulations not started (status=-1).

    Returns
    -------
    pathlib.Path
        Path to checkpoint file
    """
    pathCheckpoint = tempdir / ".test_sims_BPL"
    with open(pathCheckpoint, "w") as f:
        f.write(f"Vspace File: {tempdir}/bpl.in\n")
        f.write("Total Number of Simulations: 3\n")
        f.write("sim_00 -1\n")
        f.write("sim_01 -1\n")
        f.write("sim_02 -1\n")
        f.write("THE END\n")
    return pathCheckpoint


@pytest.fixture
def checkpoint_file_empty(tempdir):
    """
    Create an empty checkpoint file for edge case testing.

    Returns
    -------
    pathlib.Path
        Path to empty checkpoint file
    """
    pathCheckpoint = tempdir / ".test_sims_BPL"
    with open(pathCheckpoint, "w") as f:
        f.write(f"Vspace File: {tempdir}/bpl.in\n")
        f.write("Total Number of Simulations: 0\n")
        f.write("THE END\n")
    return pathCheckpoint
