#!/usr/bin/env python

import os
import multiprocessing as mp
import subprocess as sub
import argparse
import h5py
import numpy as np
import pandas as pd
from .bigplanet_archive import Archive
from .bigplanet_filter import Filter


def Main(bpInputFile, cores, quiet, overwrite, verbose, archive):
    # folder,bplArchive,output,bodyFileList,primaryFile,IncludeList,ExcludeList,Ulysses = ReadFile(file,verbose)
    #
    # if if IncludeList != [] and ExcludeList != [] and os.path.isfile(bplArchive) == False:
    #     print("Creating Archive BLA file...")
    #     MainMethodA(bpInputFile,cores,quiet,email,force,verbose)
    # else:
    #     print("Creating filtered BPF file...")
    #     MainMethodF(bpInputFile,quiet,verbose)

    if archive == True:
        print("Creating Archive BPA file...")
        Archive(bpInputFile, cores, quiet, overwrite, verbose)
    else:
        print("Creating filtered BPF file...")
        Filter(bpInputFile, quiet, verbose)


def Arguments():
    max_cores = mp.cpu_count()
    parser = argparse.ArgumentParser(
        description="Extract data from Vplanet simulations")
    parser.add_argument(
        "bpInputFile", help="Name of the biugplanet input file")
    parser.add_argument("-c", "--cores", type=int,
                        default=max_cores, help="Number of processors used")
    parser.add_argument("-o", "--overwrite", action="store_true",
                        help="overwrite archive file if it already exists")
    parser.add_argument("-a", "--archive", action="store_true",
                        help="flag for archive file creation")

    # adds the quiet and verbose as mutually exclusive groups
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-q", "--quiet", action="store_true",
                       help="no output for bigplanet")
    group.add_argument("-v", "--verbose", action="store_true",
                       help="Prints out excess output for bigplanet")

    args = parser.parse_args()

    Main(args.bpInputFile, args.cores, args.quiet,
         args.overwrite, args.verbose, args.archive)
