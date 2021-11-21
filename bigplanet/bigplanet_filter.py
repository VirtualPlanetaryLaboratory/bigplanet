#!/usr/bin/env python

import os
import multiprocessing as mp
import subprocess as sub
import argparse
import h5py
import numpy as np
import csv
import pathlib
import sys
import pandas as pd
from .bp_process import *
from .bp_get import *
from .bp_extract import *


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
        spl = item.rpartition(':')
        if spl[-1] == "initial" or spl[-1] == "final" or spl[-1] == 'OutputOption' or spl[-1] == 'GridOutputOption':
            loglist.append(item)
        # check if its forward or any of the statsitical functions
        elif (
            spl[-1] == "forward" or spl[-1] == "mean" or spl[-1] == "mode" or spl[-1] == "max" or
            spl[-1] == "min" or spl[-1] == "geomean" or spl[-1] == "stddev"
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


def Filter(file, quiet, verbose):
    folder, bplArchive, output, bodyFileList, primaryFile, IncludeList, ExcludeList, Ulysses, SimName = ReadFile(
        file, verbose=True, archive=False)

    vplHelp = GetVplanetHelp()

    infile_list = []
    for i in bodyFileList:
        infile_list.append(i)
    infile_list = bodyFileList
    infile_list.append(primaryFile)

    # if the bpl archive file does NOT exist, we have to get the data manually
    if os.path.isfile(bplArchive) == False:
        print("WARNING: BPA File does not exist. Obtaining data from source folder. This make take some time...")
        # first we need to see what keys go to what vplanet file (ie body file or log file or forward file)
        if IncludeList:

            loglist, optionList, forwardlist, climatelist, backwardlist = SplitsaKey(
                IncludeList, verbose)
            # now that we have the list of which keys to look for in which files, we can process the files and grab the data
            if SimName:
                simList = GetSims(folder, simname=SimName)
            else:
                simList = GetSims(folder)

            system_name, body_names = GetSNames(infile_list, simList)

            log_file = GetLogName(infile_list, simList, system_name)
            data = {}
            for sim in simList:
                if loglist:
                    if verbose:
                        print("Processing Log file", log_file)
                    # we need to get the system name to get the name of the logfile
                    data = ProcessLogFile(
                        log_file, data, sim, verbose, incl=IncludeList)
                    print(data)

                if optionList:
                    # we need to get the vplanet help and process the particular log file it came in
                    for k in infile_list:
                        if verbose:
                            print("Processing input file", k)
                        data = ProcessInputfile(
                            data, k, sim, vplHelp, verbose, incl=IncludeList)
                if forwardlist:
                    print("Forward file data requested")
                    for body in body_names:
                        print(body)
                        if any(body in s for s in forwardlist) == False:
                            continue
                        else:
                            outfile = body + ":sOutFile:option"
                            # check bodyfile for sOutfile to see if the name is set for the forward file otherwise
                            # its the same as default

                            if outfile in data:
                                forward_name = data[outfile]
                            else:
                                forward_name = system_name + '.' + body + '.forward'

                            header = [body + ':' + 'OutputOrder']
                            heading = {}
                            print("Obtaining Header for Logfile...")
                            heading = ProcessLogFile(
                                log_file, heading, sim, verbose, incl=header)

                            print("Processing Forward File", forward_name)
                            data = ProcessOutputfile(
                                forward_name, data, body, heading, ':forward', sim, verbose, incl=IncludeList)

                if backwardlist:
                    print("Processing Backwards File")
                    for body in body_names:
                        if any(body in s for s in backwardlist) == False:
                            continue
                        outfile = body + ":sOutFile:option"
                        # check bodyfile for sOutfile to see if the name is set for the forward file otherwise
                        # its the same as default

                        if outfile in data:
                            backward_name = data[outfile]
                        else:
                            backward_name = system_name + '.' + body + '.backward'

                        header = [body + ':' + 'OutputOrder']
                        heading = {}
                        heading = ProcessLogFile(
                            log_file, heading, sim, verbose, incl=header)
                        data = ProcessOutputfile(
                            backward_name, data, body, heading, ':backward', sim, verbose, incl=IncludeList)
                if climatelist:
                    for body in body_names:
                        if any(body in s for s in climatelist) == False:
                            continue
                        else:
                            header = [body + ':' + 'GridOutputOrder']
                            climate_name = system_name + '.' + body + '.Climate'

                            heading = {}
                            heading = ProcessLogFile(
                                log_file, heading, sim, verbose, incl=header)
                            data = ProcessOutputfile(
                                climate_name, data, body, heading, ':climate', sim, verbose, incl=IncludeList)

            if Ulysses == 1:
                DictToCSV(data, ulysses=True)
            else:
                with h5py.File(output, 'w') as filter:
                    # Change this to DictToBP <- this reads from Dict to Bigplanet File
                    DictToBP(data, vplHelp, filter, verbose,
                             group_name=None, archive=False)
    # if the bpl file DOES exist, we just need to open it and extract the data to put it in the filter file
    else:
        print("Extracting data from BPA File. Please wait...")
        archive = BPLFile(bplArchive)
        if Ulysses == 1:
            if SimName:
                ArchiveToCSV(archive, IncludeList, output,
                             ulysses=1, group=SimName)
            else:
                # Change this to ArchiveToCSV <- this reads from archive file and exports a CSV
                ArchiveToCSV(archive, IncludeList, output, ulysses=1)
        else:
            # Change this to ArchiveToBPF <- this reads from Archive to Filterd File
            ArchiveToFiltered(archive, IncludeList, output)
