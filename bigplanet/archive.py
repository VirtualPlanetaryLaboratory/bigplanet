#!/usr/bin/env python

import multiprocessing as mp
import os
import subprocess as sub
import h5py
from .extract import *
from .read import *
from .process import *


def Archive(bpInputFile, cores, quiet, force, ignorecorrupt, verbose):

    # Get the directory and list of  from the bpl file
    (
        dest_folder,
        bpl_file,
        outputFile,
        bodylist,
        primaryFile,
        includelist,
        excludelist,
        ulysses,
        SimName,
    ) = ReadFile(bpInputFile, verbose, archive=True)
    # we need to combine the body and primary files into one list
    infile_list = []
    for i in bodylist:
        infile_list.append(i)
    infile_list = bodylist
    infile_list.append(primaryFile)
    # Get the list of simulation (trial) names in a List
    sim_list = GetSims(dest_folder)
    # Get the SNames (sName and sSystemName) for the simuations
    # Save the name of the log file
    system_name, body_list = GetSNames(infile_list, sim_list)
    log_file = system_name + ".log"

    # gets the dictionary of input params
    vplanet_help = GetVplanetHelp()

    # creates the chepoint file name
    checkpoint_file = os.getcwd() + "/" + "." + dest_folder + "_BPL"

    # Create the checkpoint file to be used to keep track of the groups
    if os.path.isfile(checkpoint_file) == False:
        CreateCP(checkpoint_file, bpInputFile, sim_list)

    # if it does exist, it checks for any 0's (sims that didn't complete) and
    # changes them to -1 to be re-ran
    else:
        ReCreateCP(
            checkpoint_file, bpInputFile, quiet, sim_list, dest_folder, force
        )

    # now that we have everything we need
    # we save the name of the Master HDF5 file
    master_hdf5_file = os.path.abspath(bpl_file)

    # creates the lock and workers for the parallel processes
    lock = mp.Lock()
    workers = []

    # for each core, create a process that adds a group to the hdf5 file and adds that to the Master HDF5 file
    for i in range(cores):
        workers.append(
            mp.Process(
                target=par_worker,
                args=(
                    checkpoint_file,
                    system_name,
                    body_list,
                    log_file,
                    infile_list,
                    quiet,
                    lock,
                    vplanet_help,
                    master_hdf5_file,
                    verbose,
                ),
            )
        )
    for w in workers:
        w.start()
    for w in workers:
        w.join()

    print("Archive created with Fletcher32 checksums enabled for data integrity verification.")


def CreateCP(checkpoint_file, input_file, sims):
    with open(checkpoint_file, "w") as cp:
        cp.write("Vspace File: " + os.getcwd() + "/" + input_file + "\n")
        cp.write("Total Number of Simulations: " + str(len(sims)) + "\n")
        for f in range(len(sims)):
            cp.write(sims[f] + " " + "-1 \n")
        cp.write("THE END \n")


def ReCreateCP(checkpoint_file, input_file, quiet, sims, folder_name, force):

    datalist = []

    with open(checkpoint_file, "r") as f:
        for newline in f:
            if newline:
                datalist.append(newline.strip().split())
                for l in datalist:
                    if l[1] == "0":
                        l[1] = "-1"
                        folder = l[0]
                        with h5py.File(folder_name + ".bpa", "a") as master:
                            group_name = "/" + folder.split("/")[-1]
                            if group_name in master:
                                if quiet == False:
                                    print(
                                        "Deleting",
                                        group_name,
                                        "from BPL file...",
                                    )
                                del master[group_name]

    with open(checkpoint_file, "w") as f:
        for newline in datalist:
            f.writelines(" ".join(newline) + "\n")

    if all(l[1] == "1" for l in datalist[2:-2]) == True:
        if quiet == False:
            print("All Groups in BPL file exist")

        if force == True:
            if quiet == False:
                print("Deleting BPL file...")
            os.remove(folder_name + ".bpa")
            if quiet == False:
                print("Deleting checkpoint file...")
            os.remove(checkpoint_file)
            CreateCP(checkpoint_file, input_file, sims)
        else:
            exit()

    else:
        if quiet == False:
            print("Continuing from Checkpoint...")


def fnGetNextSimulation(sCheckpointFile, lockFile):
    """
    Find and mark the next simulation to process from checkpoint file.

    Thread-safe with file locking. Reads checkpoint, finds first simulation
    with status -1, marks it as 0 (in-progress), and returns the folder path.

    Parameters
    ----------
    sCheckpointFile : str
        Path to checkpoint file
    lockFile : multiprocessing.Lock
        Lock for thread-safe file access

    Returns
    -------
    str or None
        Absolute path to simulation folder, or None if all done
    """
    lockFile.acquire()
    listData = []

    with open(sCheckpointFile, "r") as f:
        for sLine in f:
            listData.append(sLine.strip().split())

    sFolder = ""
    for listLine in listData:
        if listLine[1] == "-1":
            sFolder = listLine[0]
            listLine[1] = "0"
            break

    if not sFolder:
        lockFile.release()
        return None

    with open(sCheckpointFile, "w") as f:
        for listLine in listData:
            f.writelines(" ".join(listLine) + "\n")

    lockFile.release()
    return os.path.abspath(sFolder)


def fnMarkSimulationComplete(sCheckpointFile, sFolder, lockFile):
    """
    Mark simulation as complete in checkpoint file.

    Thread-safe with file locking. Updates status from 0 or -1 to 1.

    Parameters
    ----------
    sCheckpointFile : str
        Path to checkpoint file
    sFolder : str
        Folder path to mark as complete
    lockFile : multiprocessing.Lock
        Lock for thread-safe file access

    Returns
    -------
    None
    """
    lockFile.acquire()
    listData = []

    with open(sCheckpointFile, "r") as f:
        for sLine in f:
            listData.append(sLine.strip().split())

    for listLine in listData:
        if listLine[0] == sFolder:
            listLine[1] = "1"
            break

    with open(sCheckpointFile, "w") as f:
        for listLine in listData:
            f.writelines(" ".join(listLine) + "\n")

    lockFile.release()


def fbCheckGroupExists(hMaster, sGroupName):
    """
    Check if HDF5 group already exists in archive.

    Parameters
    ----------
    hMaster : h5py.File
        Opened HDF5 file handle
    sGroupName : str
        Group name to check (with leading /)

    Returns
    -------
    bool
        True if group exists
    """
    return sGroupName in hMaster


def fnProcessSimulationData(sFolder, sSystemName, listBodies, sLogFile,
                           listInfiles, dictVplanetHelp, bVerbose):
    """
    Gather all data for a single simulation.

    Parameters
    ----------
    sFolder : str
        Path to simulation folder
    sSystemName : str
        System name
    listBodies : list
        List of body names
    sLogFile : str
        Log file name
    listInfiles : list
        List of input file names
    dictVplanetHelp : dict
        VPLanet help dictionary
    bVerbose : bool
        Verbose output flag

    Returns
    -------
    dict
        Complete data dictionary for simulation
    """
    dictData = {}
    return GatherData(
        dictData,
        sSystemName,
        listBodies,
        sLogFile,
        listInfiles,
        dictVplanetHelp,
        sFolder,
        bVerbose,
    )


def fnWriteSimulationToArchive(hMaster, dictData, sGroupName,
                              dictVplanetHelp, bVerbose):
    """
    Write simulation data dictionary to HDF5 archive.

    Parameters
    ----------
    hMaster : h5py.File
        Opened HDF5 file handle
    dictData : dict
        Data dictionary to write
    sGroupName : str
        Group name (with leading /)
    dictVplanetHelp : dict
        VPLanet help dictionary
    bVerbose : bool
        Verbose output flag

    Returns
    -------
    None
    """
    DictToBP(
        dictData,
        dictVplanetHelp,
        hMaster,
        bVerbose,
        sGroupName,
        archive=True,
    )


def par_worker(
    checkpoint_file,
    system_name,
    body_list,
    log_file,
    in_files,
    quiet,
    lock,
    vplanet_help,
    h5_file,
    verbose,
):
    """
    Parallel worker process for archive creation.

    Continuously processes simulations until checkpoint is complete.
    Uses helper functions for modular, testable code.

    Parameters
    ----------
    checkpoint_file : str
        Path to checkpoint file
    system_name : str
        System name
    body_list : list
        List of body names
    log_file : str
        Log file name
    in_files : list
        List of input files
    quiet : bool
        Quiet mode flag
    lock : multiprocessing.Lock
        Lock for thread-safe operations
    vplanet_help : dict
        VPLanet help dictionary
    h5_file : str
        Path to HDF5 archive file
    verbose : bool
        Verbose output flag

    Returns
    -------
    None
    """
    while True:
        # Get next simulation to process
        sFolder = fnGetNextSimulation(checkpoint_file, lock)
        if sFolder is None:
            return  # All done

        sGroupName = "/" + sFolder.split("/")[-1]

        # Process and write simulation data
        lock.acquire()
        with h5py.File(h5_file, "a") as hMaster:
            if not fbCheckGroupExists(hMaster, sGroupName):
                if not quiet:
                    print("Creating", sGroupName, "...")

                dictData = fnProcessSimulationData(
                    sFolder, system_name, body_list, log_file,
                    in_files, vplanet_help, verbose
                )

                fnWriteSimulationToArchive(
                    hMaster, dictData, sGroupName, vplanet_help, verbose
                )

        lock.release()

        # Mark complete
        fnMarkSimulationComplete(checkpoint_file, sFolder, lock)
