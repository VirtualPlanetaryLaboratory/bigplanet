"""
Test data generators for BigPlanet tests.

This module provides utilities to generate realistic test data for VPLanet
simulations without requiring external dependencies.
"""

import os
import pathlib
from typing import Dict, List, Optional, Tuple

import numpy as np


def fnCreateMinimalSimulation(
    pathSimDir: pathlib.Path,
    sSystemName: str = "earth",
    listBodyNames: Optional[List[str]] = None,
    iNumTimeSteps: int = 6,
    bIncludeForward: bool = True,
    bIncludeClimate: bool = False
) -> None:
    """
    Create a minimal VPLanet simulation directory for testing.

    Parameters
    ----------
    pathSimDir : pathlib.Path
        Directory where simulation files will be created
    sSystemName : str, optional
        System name (default "earth")
    listBodyNames : list of str, optional
        Body names (default ["sun", "earth"])
    iNumTimeSteps : int, optional
        Number of time steps in forward files (default 6)
    bIncludeForward : bool, optional
        Whether to include forward evolution files (default True)
    bIncludeClimate : bool, optional
        Whether to include climate files (default False)
    """
    if listBodyNames is None:
        listBodyNames = ["sun", "earth"]

    pathSimDir.mkdir(parents=True, exist_ok=True)

    # Create vpl.in (primary file)
    fnCreateVplIn(pathSimDir, sSystemName, listBodyNames)

    # Create body files
    for sBody in listBodyNames:
        if sBody == "sun":
            fnCreateSunIn(pathSimDir)
        else:
            fnCreateBodyIn(pathSimDir, sBody, bIncludeForward, bIncludeClimate)

    # Create log file
    fnCreateLogFile(pathSimDir, sSystemName, listBodyNames, bIncludeForward, bIncludeClimate)

    # Create forward files if requested
    if bIncludeForward:
        for sBody in listBodyNames:
            if sBody != "sun":
                fnCreateForwardFile(pathSimDir, sSystemName, sBody, iNumTimeSteps)


def fnCreateVplIn(
    pathSimDir: pathlib.Path,
    sSystemName: str,
    listBodyNames: List[str]
) -> None:
    """Create vpl.in primary input file."""
    sBodyFiles = " ".join([f"{sBody}.in" for sBody in listBodyNames])

    sContent = f"""# Primary input file
sSystemName	{sSystemName}
sPrimaryFile	vpl.in
saBodyFiles	{sBodyFiles}

sUnitMass	kg
sUnitLength	m
sUnitTime	sec
sUnitAngle	rad

dStopTime	5e9
dOutputTime	1e8

bOverwrite	1
bDoForward	1
"""
    pathFile = pathSimDir / "vpl.in"
    pathFile.write_text(sContent)


def fnCreateSunIn(pathSimDir: pathlib.Path) -> None:
    """Create sun.in stellar body file."""
    sContent = """# Stellar parameters
sName		sun
saModules 	stellar

# Physical Properties
dMass		1.0
dAge		1e6
dRotPeriod	-1.0

saOutputOrder -Time -Luminosity -Radius
"""
    pathFile = pathSimDir / "sun.in"
    pathFile.write_text(sContent)


def fnCreateBodyIn(
    pathSimDir: pathlib.Path,
    sBodyName: str,
    bIncludeForward: bool,
    bIncludeClimate: bool
) -> None:
    """Create a planetary body input file."""
    sOutputOrder = "-Time -TMan -TCore -Eccentricity -Obliquity"
    sGridOutput = ""
    sOutFile = ""

    if bIncludeForward:
        sOutFile = f"\nsOutFile {sBodyName}.{sBodyName}.forward"

    if bIncludeClimate:
        sGridOutput = "\nsaGridOutput -DailyInsol -SeasonalTemp"

    sContent = f"""# {sBodyName} parameters
sName		{sBodyName}
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
dTCore         6000{sOutFile}

saOutputOrder {sOutputOrder}{sGridOutput}
"""
    pathFile = pathSimDir / f"{sBodyName}.in"
    pathFile.write_text(sContent)


def fnCreateLogFile(
    pathSimDir: pathlib.Path,
    sSystemName: str,
    listBodyNames: List[str],
    bIncludeForward: bool,
    bIncludeClimate: bool
) -> None:
    """Create a VPLanet log file."""
    sBodyFiles = "\n".join([f"Body File #{i+1}: {sBody}.in"
                           for i, sBody in enumerate(listBodyNames)])

    sContent = f"""-------- Log file {sSystemName}.log -------

Executable: /usr/local/bin/vplanet
Version: 1.0.0
System Name: {sSystemName}
Primary Input File: vpl.in
{sBodyFiles}

---- INITIAL SYSTEM PROPERTIES ----
(Age) System Age [sec]: 0.000000
(Time) Simulation Time [sec]: 0.000000
(TotAngMom) Total Angular Momentum [kg*m^2/sec]: 1.474456e+42

"""

    # Add body sections
    for sBody in listBodyNames:
        if sBody == "sun":
            sContent += fnGetSunLogSection(bInitial=True)
        else:
            sContent += fnGetBodyLogSection(sBody, True, bIncludeForward, bIncludeClimate)

    sContent += """
---- FINAL SYSTEM PROPERTIES ----
(Age) System Age [sec]: 1.577880e+17
(Time) Simulation Time [sec]: 1.577880e+17
(TotAngMom) Total Angular Momentum [kg*m^2/sec]: 1.474456e+42

"""

    # Add final body sections
    for sBody in listBodyNames:
        if sBody == "sun":
            sContent += fnGetSunLogSection(bInitial=False)
        else:
            sContent += fnGetBodyLogSection(sBody, False, bIncludeForward, bIncludeClimate)

    pathFile = pathSimDir / f"{sSystemName}.log"
    pathFile.write_text(sContent)


def fnGetSunLogSection(bInitial: bool) -> str:
    """Generate sun section of log file."""
    if bInitial:
        fLuminosity = 3.846000e+26
        fRadius = 2.019571e+08
    else:
        fLuminosity = 3.950000e+26
        fRadius = 2.050000e+08

    return f"""----- BODY: sun ----
Active Modules: STELLAR
(Mass) Mass [kg]: 1.988416e+30
(Radius) Radius [m]: {fRadius:.6e}
(RotPer) Rotational Period [sec]: 8.640000e+04
(Luminosity) Luminosity [kg*m^2/sec^3]: {fLuminosity:.6e}
Output Order: Time [sec] Luminosity [kg*m^2/sec^3] Radius [m]
Grid Output Order:

"""


def fnGetBodyLogSection(
    sBody: str,
    bInitial: bool,
    bIncludeForward: bool,
    bIncludeClimate: bool
) -> str:
    """Generate planetary body section of log file."""
    if bInitial:
        fTMan = 3000.0
        fTCore = 6000.0
        fObl = 0.408407
        fEcc = 0.0167
    else:
        fTMan = 2750.0
        fTCore = 5500.0
        fObl = 0.406000
        fEcc = 0.0158

    sOutputOrder = "Time [sec] TMan [K] TCore [K] Eccentricity [] Obliquity [rad]"
    sGridOutput = ""

    if bIncludeClimate:
        sGridOutput = "DailyInsol [W/m^2] SeasonalTemp [deg C]"

    return f"""----- BODY: {sBody} ----
Active Modules: RadHeat ThermInt
(Mass) Mass [kg]: 5.972e+24
(Radius) Radius [m]: 6.371e+06
(Obliquity) Obliquity [rad]: {fObl:.6f}
(Eccentricity) Orbital Eccentricity []: {fEcc:.4f}
(TMan) Upper Mantle Temperature [K]: {fTMan:.1f}
(TCore) Core Temperature [K]: {fTCore:.1f}
(Instellation) Orbit-averaged INcident STELLar radiATION [M_sun*AU^2/year^3]: 1.937119e+33
Output Order: {sOutputOrder}
Grid Output Order: {sGridOutput}

"""


def fnCreateForwardFile(
    pathSimDir: pathlib.Path,
    sSystemName: str,
    sBodyName: str,
    iNumSteps: int
) -> None:
    """Create a forward evolution file."""
    # Generate time series data
    daTimes = np.linspace(0, 5e9, iNumSteps)
    daTMan = 3000 - 250 * (daTimes / 5e9)
    daTCore = 6000 - 500 * (daTimes / 5e9)
    daEcc = 0.0167 - 0.0009 * (daTimes / 5e9)
    daObl = 0.4084 - 0.0024 * (daTimes / 5e9)

    daData = np.column_stack([daTimes, daTMan, daTCore, daEcc, daObl])

    sFilename = f"{sSystemName}.{sBodyName}.forward"
    pathFile = pathSimDir / sFilename
    np.savetxt(pathFile, daData, fmt='%.6e')


def fnCreateMultipleSimulations(
    pathBaseDir: pathlib.Path,
    iNumSims: int,
    sTrialName: str = "sim_"
) -> List[pathlib.Path]:
    """
    Create multiple simulation directories for testing parameter sweeps.

    Parameters
    ----------
    pathBaseDir : pathlib.Path
        Base directory for simulations
    iNumSims : int
        Number of simulations to create
    sTrialName : str, optional
        Prefix for trial names (default "sim_")

    Returns
    -------
    list of pathlib.Path
        List of created simulation directories
    """
    listSimDirs = []

    for iSim in range(iNumSims):
        sSimName = f"{sTrialName}{iSim:02d}"
        pathSimDir = pathBaseDir / sSimName
        fnCreateMinimalSimulation(pathSimDir)
        listSimDirs.append(pathSimDir)

    return listSimDirs


def fnCreateVspaceIn(
    pathDir: pathlib.Path,
    sDestFolder: str,
    sTrialName: str = "sim_",
    sParamName: str = "dSemi",
    fMin: float = 0.5,
    fMax: float = 2.0,
    iNumTrials: int = 10
) -> pathlib.Path:
    """
    Create a vspace input file for parameter sweep.

    Parameters
    ----------
    pathDir : pathlib.Path
        Directory where vspace.in will be created
    sDestFolder : str
        Destination folder name for simulations
    sTrialName : str, optional
        Trial name prefix (default "sim_")
    sParamName : str, optional
        Parameter to sweep (default "dSemi")
    fMin : float, optional
        Minimum parameter value (default 0.5)
    fMax : float, optional
        Maximum parameter value (default 2.0)
    iNumTrials : int, optional
        Number of trials (default 10)

    Returns
    -------
    pathlib.Path
        Path to created vspace.in file
    """
    sContent = f"""srcfolder  .
destfolder {sDestFolder}
trialname  {sTrialName}

file   earth.in
{sParamName} [{fMin}, {fMax}, n{iNumTrials}] a

file sun.in

file vpl.in
"""
    pathFile = pathDir / "vspace.in"
    pathFile.write_text(sContent)
    return pathFile


def fnCreateBigPlanetIn(
    pathDir: pathlib.Path,
    sDestFolder: str,
    listBodyFiles: Optional[List[str]] = None,
    sPrimaryFile: str = "vpl.in",
    sArchiveFile: Optional[str] = None,
    listInclude: Optional[List[str]] = None
) -> pathlib.Path:
    """
    Create a BigPlanet input file.

    Parameters
    ----------
    pathDir : pathlib.Path
        Directory where bpl.in will be created
    sDestFolder : str
        Source folder with simulation data
    listBodyFiles : list of str, optional
        Body file names (default ["earth.in", "sun.in"])
    sPrimaryFile : str, optional
        Primary file name (default "vpl.in")
    sArchiveFile : str, optional
        Archive file name (if creating BPA)
    listInclude : list of str, optional
        Keys to include in filtered file

    Returns
    -------
    pathlib.Path
        Path to created bpl.in file
    """
    if listBodyFiles is None:
        listBodyFiles = ["earth.in", "sun.in"]

    sBodyFiles = " ".join(listBodyFiles)
    sContent = f"""sDestFolder {sDestFolder}

saBodyFiles  {sBodyFiles}
sPrimaryFile {sPrimaryFile}
"""

    if sArchiveFile:
        sContent += f"\nsArchiveFile {sArchiveFile}\n"

    if listInclude:
        sInclude = " ".join(listInclude)
        sContent += f"\nsaKeyInclude {sInclude}\n"

    pathFile = pathDir / "bpl.in"
    pathFile.write_text(sContent)
    return pathFile
