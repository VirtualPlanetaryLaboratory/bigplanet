#!/usr/bin/env python

import argparse
import multiprocessing as mp
import os
import subprocess as sub

import h5py
import numpy as np
import pandas as pd

from .archive import Archive
from .filter import Filter
from .extract import Md5CheckSum
from .read import ReadFile


def Main(
    bpInputFile,
    cores,
    quiet,
    overwrite,
    verbose,
    archive,
    deleterawdata,
    ignorecorrupt,
):
    # folder,bplArchive,output,bodyFileList,primaryFile,IncludeList,ExcludeList,Ulysses = ReadFile(file,verbose)
    #
    # if if IncludeList != [] and ExcludeList != [] and os.path.isfile(bplArchive) == False:
    #     print("Creating Archive BLA file...")
    #     MainMethodA(bpInputFile,cores,quiet,email,force,verbose)
    # else:
    #     print("Creating filtered BPF file...")
    #     MainMethodF(bpInputFile,quiet,verbose)
    if deleterawdata == True:
        # folder_name, bpl_file, outputFile, bodylist, primaryFile, includelist, excludelist, Ulysses, SimName
        (
            folder,
            bplArchive,
            output,
            bodyFileList,
            primaryFile,
            IncludeList,
            ExcludeList,
            Ulysses,
            simname,
        ) = ReadFile(bpInputFile, verbose, archive)
        if os.path.exists(bplArchive) == True:
            Md5CheckSum(bplArchive, ignorecorrupt)
            reply = None
            question = (
                "WARNING: This command will delete the "
                + folder
                + " directory along with any MultiPlanet checkpoint files."
            )
            while reply not in ("y", "n"):
                reply = str(input(question + " (y/n): ")).lower().strip()
                if reply[:1] == "y":
                    sub.run(["rm", "-rf", folder])
                    if os.path.isfile("." + folder) == True:
                        sub.run(["rm", "." + folder])
                    print("Files deleted.")
                    exit()
                if reply[:1] == "n":
                    print("Files NOT deleted. Exiting.")
                    exit()
                else:
                    print("User input was not valid. Exiting.")
                    exit()

        else:
            print("ERROR: The archive file " + bplArchive + " does not exist")

    if archive == True:
        print("Creating BPA file...")
        Archive(bpInputFile, cores, quiet, overwrite, ignorecorrupt, verbose)
    else:
        print("Creating BPF file...")
        Filter(bpInputFile, quiet, verbose, ignorecorrupt, overwrite)


def Arguments():
    max_cores = mp.cpu_count()
    parser = argparse.ArgumentParser(
        description="Extract data from Vplanet simulations"
    )
    parser.add_argument(
        "bpInputFile", help="Name of the biugplanet input file"
    )
    parser.add_argument(
        "-c",
        "--cores",
        type=int,
        default=max_cores,
        help="Number of processors used",
    )
    parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="overwrite file if it already exists",
    )
    parser.add_argument(
        "-a",
        "--archive",
        action="store_true",
        help="flag for archive file creation",
    )
    parser.add_argument(
        "-deleterawdata",
        "--deleterawdata",
        action="store_true",
        help="removes source files after creation of Bigplanet files",
    )
    parser.add_argument(
        "-ignorecorrupt",
        "--ignorecorrupt",
        action="store_true",
        help="ignore data corruption for MD5 Checksum",
    )
    # adds the quiet and verbose as mutually exclusive groups
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-q", "--quiet", action="store_true", help="no output for bigplanet"
    )
    group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Prints out excess output for bigplanet",
    )

    args = parser.parse_args()

    Main(
        args.bpInputFile,
        args.cores,
        args.quiet,
        args.overwrite,
        args.verbose,
        args.archive,
        args.deleterawdata,
        args.ignorecorrupt,
    )
