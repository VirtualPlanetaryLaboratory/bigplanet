#!/usr/bin/env python

import argparse
import csv
import multiprocessing as mp
import os
import pathlib
import subprocess as sub
import sys

import h5py
import numpy as np
import pandas as pd

from .extract import *
from .read import *
from .process import *


def fbCheckOutputExists(sOutputPath, iUlysses, bOverride):
    """Check if output file exists and determine if should proceed."""
    if iUlysses == 1:
        return True
    if os.path.isfile(sOutputPath) and not bOverride:
        print(f"ERROR: {sOutputPath} already exists. Use -o to override.")
        return False
    return True


def fnProcessLogKeys(listInclude, dictData, sSystemName, listBodyNames,
                     sLogFile, sFolder, bVerbose):
    """Process log file keys (initial/final values)."""
    if bVerbose:
        print("Processing Log file", sLogFile)
    return ProcessLogFile(
        sLogFile, dictData, sFolder, bVerbose, incl=listInclude
    )


def fnProcessOptionKeys(listInclude, listInfiles, dictData, sFolder,
                        dictVplanetHelp, bVerbose):
    """Process option/input file keys."""
    for sInfile in listInfiles:
        if bVerbose:
            print("Processing input file", sInfile)
        dictData = ProcessInputfile(
            dictData, sInfile, sFolder, dictVplanetHelp, bVerbose, incl=listInclude
        )
    return dictData


def fsGetOutputFilename(sBody, sSystemName, dictData, sFileType):
    """Determine output filename based on sOutFile or defaults."""
    sOutfileKey = sBody + ":sOutFile:option"
    if sOutfileKey in dictData:
        return dictData[sOutfileKey]
    return f"{sSystemName}.{sBody}.{sFileType}"


def fnProcessForwardKeys(listInclude, listBodyNames, dictData, sSystemName,
                         sLogFile, sFolder, bVerbose):
    """Process forward evolution file keys."""
    print("Forward file data requested")
    for sBody in listBodyNames:
        print(sBody)
        if not any(sBody in s for s in listInclude):
            continue

        sForwardName = fsGetOutputFilename(sBody, sSystemName, dictData, "forward")

        listHeader = [sBody + ":" + "OutputOrder"]
        dictHeading = {}
        print("Obtaining Header for Logfile...")
        dictHeading = ProcessLogFile(
            sLogFile, dictHeading, sFolder, bVerbose, incl=listHeader
        )

        print("Processing Forward File", sForwardName)
        dictData = ProcessOutputfile(
            sForwardName, dictData, sBody, dictHeading, ":forward",
            sFolder, bVerbose, incl=listInclude,
        )
    return dictData


def fnProcessBackwardKeys(listInclude, listBodyNames, dictData, sSystemName,
                          sLogFile, sFolder, bVerbose):
    """Process backward evolution file keys."""
    print("Processing Backwards File")
    for sBody in listBodyNames:
        if not any(sBody in s for s in listInclude):
            continue

        sBackwardName = fsGetOutputFilename(sBody, sSystemName, dictData, "backward")

        listHeader = [sBody + ":" + "OutputOrder"]
        dictHeading = {}
        dictHeading = ProcessLogFile(
            sLogFile, dictHeading, sFolder, bVerbose, incl=listHeader
        )
        dictData = ProcessOutputfile(
            sBackwardName, dictData, sBody, dictHeading, ":backward",
            sFolder, bVerbose, incl=listInclude,
        )
    return dictData


def fnProcessClimateKeys(listInclude, listBodyNames, dictData, sSystemName,
                         sLogFile, sFolder, bVerbose):
    """Process climate file keys."""
    for sBody in listBodyNames:
        if not any(sBody in s for s in listInclude):
            continue

        listHeader = [sBody + ":" + "GridOutputOrder"]
        sClimateName = f"{sSystemName}.{sBody}.Climate"

        dictHeading = {}
        dictHeading = ProcessLogFile(
            sLogFile, dictHeading, sFolder, bVerbose, incl=listHeader
        )
        dictData = ProcessOutputfile(
            sClimateName, dictData, sBody, dictHeading, ":climate",
            sFolder, bVerbose, incl=listInclude,
        )
    return dictData


def fnWriteFilteredOutput(dictData, sOutput, iUlysses, dictVplanetHelp, bVerbose):
    """Write filtered data to HDF5 or CSV."""
    if iUlysses == 1:
        DictToCSV(dictData, ulysses=True)
    else:
        with h5py.File(sOutput, "w") as hFilter:
            DictToBP(
                dictData, dictVplanetHelp, hFilter, bVerbose,
                group_name=None, archive=False,
            )


def fnExtractFromArchive(hArchive, listInclude, sOutput, iUlysses, sSimName):
    """Extract filtered data from existing archive."""
    print("Extracting data from BPA File. Please wait...")
    if iUlysses == 1:
        if sSimName:
            ArchiveToCSV(hArchive, listInclude, sOutput, ulysses=1, group=sSimName)
        else:
            ArchiveToCSV(hArchive, listInclude, sOutput, ulysses=1)
    else:
        ArchiveToFiltered(hArchive, listInclude, sOutput)


def SplitsaKey(saKeylist, verbose):
    # create empty lists to store the keys in
    loglist = []
    bodylist = []
    forwardlist = []
    climatelist = []
    backwardlist = []

    # loop over the key list
    for item in saKeylist:
        # to figure out what list they belong in, we have to rpartion them and look at the last word
        spl = item.rpartition(":")
        if (
            spl[-1] == "initial"
            or spl[-1] == "final"
            or spl[-1] == "OutputOption"
            or spl[-1] == "GridOutputOption"
        ):
            loglist.append(item)
        # check if its forward or any of the statsitical functions
        elif (
            spl[-1] == "forward"
            or spl[-1] == "mean"
            or spl[-1] == "mode"
            or spl[-1] == "max"
            or spl[-1] == "min"
            or spl[-1] == "geomean"
            or spl[-1] == "stddev"
        ):
            forwardlist.append(item)
        # checks if its a body file
        elif spl[-1] == "option":
            bodylist.append(item)
        # checks if its a climate file
        elif spl[-1] == "climate":
            climatelist.append(item)
        elif spl[-1] == "backward":
            backwardlist.append(item)
    if verbose:
        print("Log file:", loglist)
        print("Body file:", bodylist)
        print("Forward File:", forwardlist)
        print("Climate List:", climatelist)
        print("Backward List:", backwardlist)

    return loglist, bodylist, forwardlist, climatelist, backwardlist


def Filter(file, quiet, verbose, ignorecorrupt, override):
    """
    Create filtered BigPlanet file from archive or raw data.

    Orchestrates filtering by reading configuration, checking if archive
    exists (fast path) or processing raw simulation data (slow path).
    """
    (folder, bplArchive, output, bodyFileList, primaryFile, IncludeList,
     ExcludeList, Ulysses, SimName) = ReadFile(file, verbose, archive=False)

    if not fbCheckOutputExists(output, Ulysses, override):
        if Ulysses == 0:
            return

    if override and os.path.exists(output):
        print("Overriding output file...")
        sub.run(["rm", output])

    # Fast path: extract from archive if exists
    if os.path.isfile(bplArchive):
        hArchive = BPLFile(bplArchive, ignorecorrupt)
        fnExtractFromArchive(hArchive, IncludeList, output, Ulysses, SimName)
        return

    # Slow path: process from raw simulation data
    print("WARNING: BPA File does not exist. Obtaining data from source folder. This make take some time...")

    if not IncludeList:
        return

    vplHelp = GetVplanetHelp()
    infile_list = bodyFileList + [primaryFile]

    loglist, optionList, forwardlist, climatelist, backwardlist = SplitsaKey(
        IncludeList, verbose
    )

    if SimName:
        simList = GetSims(folder, simname=SimName)
    elif os.path.isfile(primaryFile):
        simList = GetSims(folder)
    else:
        simList = GetSims(folder)

    system_name, body_names = GetSNames(infile_list, simList)
    log_file = GetLogName(infile_list, simList, system_name)
    data = {}

    for sim in simList:
        if loglist:
            data = fnProcessLogKeys(IncludeList, data, system_name, body_names,
                                   log_file, sim, verbose)
            print(data)

        if optionList:
            data = fnProcessOptionKeys(IncludeList, infile_list, data, sim,
                                      vplHelp, verbose)

        if forwardlist:
            data = fnProcessForwardKeys(forwardlist, body_names, data,
                                       system_name, log_file, sim, verbose)

        if backwardlist:
            data = fnProcessBackwardKeys(backwardlist, body_names, data,
                                        system_name, log_file, sim, verbose)

        if climatelist:
            data = fnProcessClimateKeys(climatelist, body_names, data,
                                       system_name, log_file, sim, verbose)

    fnWriteFilteredOutput(data, output, Ulysses, vplHelp, verbose)
