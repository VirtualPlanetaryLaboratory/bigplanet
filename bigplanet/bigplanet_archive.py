#!/usr/bin/env python

import os
import multiprocessing as mp
import subprocess as sub
import argparse
import h5py
import numpy as np
import pandas as pd
from .bp_process import *
from .bp_get import *
from .bp_extract import *


def Archive(bpInputFile, cores, quiet, force, verbose):

    # Get the directory and list of  from the bpl file
    dest_folder, bpl_file, outputFile, bodylist, primaryFile, includelist, excludelist, ulysses, SimName = ReadFile(
        bpInputFile, verbose, archive=True)
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
    checkpoint_file = os.getcwd() + '/' + '.' + dest_folder + '_BPL'

    # Create the checkpoint file to be used to keep track of the groups
    if os.path.isfile(checkpoint_file) == False:
        CreateCP(checkpoint_file, bpInputFile, sim_list)

    # if it does exist, it checks for any 0's (sims that didn't complete) and
    # changes them to -1 to be re-ran
    else:
        ReCreateCP(checkpoint_file, bpInputFile,
                   quiet, sim_list, dest_folder, force)

    # now that we have everything we need
    # we save the name of the Master HDF5 file
    master_hdf5_file = os.path.abspath(dest_folder + '.bpa')

    # creates the lock and workers for the parallel processes
    lock = mp.Lock()
    workers = []

    # for each core, create a process that adds a group to the hdf5 file and adds that to the Master HDF5 file
    for i in range(cores):
        workers.append(mp.Process(target=par_worker,
                       args=(checkpoint_file, system_name, body_list, log_file, infile_list, quiet, lock, vplanet_help, master_hdf5_file, verbose)))
    for w in workers:
        w.start()
    for w in workers:
        w.join()


def CreateCP(checkpoint_file, input_file, sims):
    with open(checkpoint_file, 'w') as cp:
        cp.write('Vspace File: ' + os.getcwd() + '/' + input_file + '\n')
        cp.write('Total Number of Simulations: ' + str(len(sims)) + '\n')
        for f in range(len(sims)):
            cp.write(sims[f] + " " + "-1 \n")
        cp.write('THE END \n')


def ReCreateCP(checkpoint_file, input_file, quiet, sims, folder_name, force):

    datalist = []

    with open(checkpoint_file, 'r') as f:
        for newline in f:
            if newline:
                datalist.append(newline.strip().split())
                for l in datalist:
                    if l[1] == '0':
                        l[1] = '-1'
                        folder = l[0]
                        with h5py.File(folder_name + '.bpa', "a") as master:
                            group_name = "/" + folder.split('/')[-1]
                            if group_name in master:
                                if quiet == False:
                                    print("Deleting", group_name,
                                          "from BPL file...")
                                del master[group_name]

    with open(checkpoint_file, 'w') as f:
        for newline in datalist:
            f.writelines(' '.join(newline)+'\n')

    if all(l[1] == '1' for l in datalist[2:-2]) == True:
        if quiet == False:
            print("All Groups in BPL file exist")

        if force == True:
            if quiet == False:
                print("Deleting BPL file...")
            os.remove(folder_name + '.bpa')
            if quiet == False:
                print("Deleting checkpoint file...")
            os.remove(checkpoint_file)
            CreateCP(checkpoint_file, input_file, sims)
        else:
            exit()

    else:
        if quiet == False:
            print('Continuing from Checkpoint...')


def par_worker(checkpoint_file, system_name, body_list, log_file, in_files, quiet, lock, vplanet_help, h5_file, verbose):

    while True:

        lock.acquire()
        datalist = []
        data = {}

        with open(checkpoint_file, 'r') as f:
            for newline in f:
                datalist.append(newline.strip().split())

        folder = ''

        for l in datalist:
            if l[1] == '-1':
                folder = l[0]
                l[1] = '0'
                break

        if not folder:
            lock.release()
            return

        with open(checkpoint_file, 'w') as f:
            for newline in datalist:
                f.writelines(' '.join(newline)+'\n')

        lock.release()

        folder = os.path.abspath(folder)

        lock.acquire()
        datalist = []

        with open(checkpoint_file, 'r') as f:
            for newline in f:
                datalist.append(newline.strip().split())

        group_name = "/" + folder.split('/')[-1]

        # creates the bpl file and reads to make sure the group name is in the file
        with h5py.File(h5_file, 'a') as Master:
            # if not then add it
            if group_name not in Master:
                if quiet == False:
                    print("Creating", group_name, "...")
                data = GatherData(data, system_name, body_list,
                                  log_file, in_files, vplanet_help, folder, verbose)
                DictToBP(data, vplanet_help, Master,
                         verbose, group_name, archive=True)

                for l in datalist:
                    if l[0] == folder:
                        l[1] = '1'
                        break
            else:
                for l in datalist:
                    if l[0] == folder:
                        l[1] = '1'
                        break

        with open(checkpoint_file, 'w') as f:
            for newline in datalist:
                f.writelines(' '.join(newline)+'\n')

        lock.release()


# def Arguments():
#     max_cores = mp.cpu_count()
#     parser = argparse.ArgumentParser(description="Extract data from Vplanet simulations")
#     parser.add_argument("bpInputFile", help="Name of the biugplanet input file")
#     parser.add_argument("-c","--cores", type=int, default=max_cores, help="Number of processors used")
#     parser.add_argument("-f","--force",action="store_true", help="Forces creation of BPL file if it already exists")
#     parser.add_argument("-s","--split",action="store_true",help="flag for filtered creation of file")
#
#     #adds the quiet and verbose as mutually exclusive groups
#     group = parser.add_mutually_exclusive_group()
#     group.add_argument("-q","--quiet", action="store_true", help="no output for bigplanet")
#     group.add_argument("-v","--verbose",action="store_true", help="Prints out excess output for bigplanet")
#
#
#     args = parser.parse_args()
#
#     Main(args.bpInputFile,args.cores,args.quiet,args.force,args.verbose,args.split)
#
#
# if __name__ == "__main__":
#     Arguments()
