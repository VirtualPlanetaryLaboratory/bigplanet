#!/usr/bin/env python

import os
import multiprocessing as mp
import sys
import subprocess as sub
import mmap
import argparse
import h5py
import numpy as np
from collections import OrderedDict
import csv
import pandas as pd
from scipy import stats



"""
Code for command line call of bigplanet
"""

def GetDir(input_file):
    """ Give it input file and returns name of folder where simulations are located. """
    infiles = []
    # gets the folder name with all the sims
    with open(input_file, 'r') as vpl:
        content = [line.strip().split() for line in vpl.readlines()]
        for line in content:
            if line:
                if line[0] == 'destfolder':
                    folder_name = line[1]

                if line[0] == 'file':
                    infiles.append(line[1])
    if folder_name is None:
        raise IOError("Name of destination folder not provided in file '%s'."
                      "Use syntax 'destfolder <foldername>'"%inputf)


    if os.path.isdir(folder_name) == False:
        print("ERROR: Folder", folder_name, "does not exist in the current directory.")
        exit()

    return folder_name, infiles

def GetSims(folder_name):
    """ Pass it folder name where simulations are and returns list of simulation folders. """
    #gets the list of sims
    sims = sorted([f.path for f in os.scandir(folder_name) if f.is_dir()])
    return sims

def parallel_run_planet(input_file, cores,quiet,email):
    # gets the folder name with all the sims
    folder_name, infiles = GetDir(input_file)
    #gets the list of sims
    sims = GetSims(folder_name)
    #initalizes the checkpoint file
    checkpoint_file = os.getcwd() + '/' + '.' + folder_name + '_hdf5'

    #checks if the files doesn't exist and if so then it creates it
    if os.path.isfile(checkpoint_file) == False:
        CreateCP(checkpoint_file,input_file,quiet,sims)

    #if it does exist, it checks for any 0's (sims that didn't complete) and
    #changes them to -1 to be re-ran
    else:
        ReCreateCP(checkpoint_file,input_file,quiet,sims)

    #get system and the body names
    body_names = []

    for file in infiles:
        #gets path to infile
        full_path = os.path.join(sims[0],file)
        #if the infile is the vpl.in, then get the system name
        if "vpl.in" in file:
            with open(full_path, 'r') as vpl:
                content = [line.strip().split() for line in vpl.readlines()]
                for line in content:
                    if line:
                        if line[0] == 'sSystemName':
                            system_name = line[1]
            logfile = system_name + ".log"
        else:
            with open(full_path, 'r') as infile:
                content = [line.strip().split() for line in infile.readlines()]
                for line in content:
                    if line:
                        if line[0] == 'sName':
                            body_names.append(line[1])

    lock = mp.Lock()
    workers = []
    for i in range(cores):
        workers.append(mp.Process(target=par_worker, args=(checkpoint_file,system_name,body_names, logfile,quiet,lock)))
    for w in workers:
        w.start()
    for w in workers:
        w.join()

    CreateMasterHDF5(folder_name,sims)

    if email is not None:
        SendMail(email, folder_name)

def SendMail(email,destfolder):
    Title = "Bigplanet has finished for " + destfolder
    Body = "Please log into your computer to verify the results. This is an auto-generated message."
    message = "echo " + Body + " | " + 'mail -s ' + '"'+ Title + '" ' + email
    sub.Popen(message , shell=True)

def CreateCP(checkpoint_file,input_file,quiet,sims):
    with open(checkpoint_file,'w') as cp:
        cp.write('Vspace File: ' + os.getcwd() + '/' + input_file + '\n')
        cp.write('Total Number of Simulations: '+ str(len(sims)) + '\n')
        for f in range(len(sims)):
            cp.write(sims[f] + " " + "-1 \n")
        cp.write('THE END \n')


def ReCreateCP(checkpoint_file,input_file,quiet,sims):
    if quiet == False:
        print('WARNING: multi-planet checkpoint file already exists!')
        print('Checking if checkpoint file is corrupt...')

    datalist = []

    with open(checkpoint_file, 'r') as f:
        for newline in f:
            if newline:
                datalist.append(newline.strip().split())
                for l in datalist:
                    if l[1] == '0':
                        l[1] = '-1'

    with open(checkpoint_file, 'w') as f:
        for newline in datalist:
            f.writelines(' '.join(newline)+'\n')



def ProcessLogFile(logfile, data):
    prop = ''
    body = 'system'

    with open(logfile, 'r') as log:
        content = [line.strip() for line in log.readlines()]

    for line in content:

        if len(line) == 0:
            continue

        if line.startswith('-'):
            tmp_line = line.replace('-', '').replace(':', '').strip().replace(' ', '_')

            if tmp_line.startswith('INITIAL_SYSTEM_PROPERTIES'):
                prop = 'initial'

            if tmp_line.startswith('FINAL_SYSTEM_PROPERTIES'):
                prop = 'final'
                body = 'system'

            if tmp_line.startswith('BODY'):
                body = tmp_line[tmp_line.find('_')+1:].strip()

            continue

        if line.startswith('('):
            fv_param = line[1:line.find(')')].strip()
            units = line[line.find('[')+1:line.find(']')].strip()

            if not units:
                units = 'nd'

            fv_value = line[line.find(':')+1:].strip()
            key_name = body + '_' +  fv_param + '_' + prop

            if key_name in data:
                data[key_name].append(fv_value)

            else:
                data[key_name] = [units, fv_value]

        if line.startswith('Output Order') and len(line[line.find(':'):]) > 1:
            parm_key = line[:line.find(':')].replace(' ', '')
            params = line[line.find(':') + 1:].strip().split(']')
            key_name = body + '_' + parm_key
            out_params = []

            for i in params:
                var = i[:i.find('[')].strip()
                units = i[i.find('[') + 1:]

                #print("V: <", var, "> U: <", units, ">")

                if not units:
                    units = 'nd'

                if var == '':
                    continue

                out_params.append([var, units])

                key_name_forward = body + '_' + var + '_forward'

                if key_name_forward not in data:
                    data[key_name_forward] = [units]

            if key_name not in data:
                data[key_name] = out_params

        if line.startswith('Grid Output Order') and len(line[line.find(':'):]) > 1:
            parm_key = line[:line.find(':')].replace(' ', '')
            params = line[line.find(':') + 1:].strip().split(']')
            key_name = body + '_' + parm_key
            out_params = []

            for i in params:
                var = i[:i.find('[')].strip()
                units = i[i.find('[') + 1:]

                if not units:
                    units = 'nd'

                if var == '':
                    continue

                out_params.append([var, units])

                key_name_climate = body + '_' + var + '_climate'

                if key_name_climate not in data:
                    data[key_name_climate] = [units]

            if key_name not in data:
                data[key_name] = out_params

    return data

def ProcessInfile(infile, file, data):
    with open(infile, 'r') as inf:
        content = [line.strip() for line in inf.readlines()]
        cont = False

        for line in content:

            if len(line) == 0 or line.startswith('#'):
                continue

            tmp_line = line[:line.find('#')].strip()

            if cont:
                fv_value = fv_value.append(tmp_line.split())
                cont = False
                continue

            fv_param = tmp_line.split()[0]
            fv_value = tmp_line.split()[1:]

            if (fv_param == 'saOutputOrder' or fv_param == 'saGridOutput') and fv_value[-1] == '$':
                cont = True

def ProcessForwardfile(forwardfile, data, body, OutputOrder):

    header = []

    for i in OutputOrder:
        header.append([i][0][0])

    sorted = np.loadtxt(forwardfile, unpack=True, dtype=str,encoding=None)

    for i,row in enumerate(sorted):
        key_name = body + '_' + header[i] + '_forward'
        data[key_name].append(row)


    return data

def ProcessClimatefile(climatefile, data, body, GridOutputOrder):

    header = []

    for i in GridOutputOrder:
        header.append([i][0][0])

    sorted = np.loadtxt(climatefile, unpack=True, dtype=str,encoding=None)

    for i,row in enumerate(sorted):
        key_name = body + '_' + header[i] + '_climate'
        data[key_name].append(row)

    return data

def ProcessSeasonalClimatefile(prefix, data, body, name):
    file = list(csv.reader(open('SeasonalClimateFiles/' + prefix + '.' + name + '.0')))
    key_name = body + '_' + name
    units = ''
    if (name == 'DailyInsol' or name == 'SeasonalFIn' or
    name == 'SeasonalFOut'or name == 'SeasonalDivF'):
        units = 'W/m^2'
    if name == 'PlanckB':
        units = 'W/m^2/K'
    if name == 'SeasonalIceBalance':
        units = 'kg/m^2/s'
    if name == 'SeasonalTemp':
        units = 'deg C'
    if name == 'SeasonalFMerid':
        units = 'W'

    if key_name not in data:
        data[key_name]= [units, file]
    else:
        data[key_name].append(file)

    return data

def CreateHDF5(data, system_name, body_names, logfile, quiet, h5filename):
    """
    ....
    """
    if quiet == False:
        print('Creating',h5filename)
        sys.stdout.flush()

    data = ProcessLogFile(logfile, data)
    for body in body_names:
        outputorder = body + "_OutputOrder"
        gridoutputorder = body + "_GridOutputOrder"

        if outputorder in data:
            OutputOrder = data[outputorder]
            forward_name = system_name + '.' + body + '.forward'
            data = ProcessForwardfile(forward_name, data, body, OutputOrder)


        if gridoutputorder in data:
            GridOutputOrder = data[gridoutputorder]
            climate_name = system_name + '.' + body + '.Climate'
            data = ProcessClimatefile(climate_name, data, body, GridOutputOrder)
            prefix = system_name + '.' + body
            name = ['DailyInsol','PlanckB','SeasonalDivF','SeasonalFIn',
                    'SeasonalFMerid','SeasonalFOut','SeasonalIceBalance',
                    'SeasonalTemp']
            for i in range(len(name)):
                data = ProcessSeasonalClimatefile(prefix,data,body,name[i])

    with h5py.File(h5filename, 'w') as h:
        for k, v in data.items():
            #print("Key:",k)
            #print("Length of Value:",len(v))
            if len(v) == 2:
                v_attr = v[0]
                v_value = [v[1]]

            else:
                v_value = v[0]
                v_attr = ''
            #print("Units:",v_attr)
            #print("Value:",v_value)
            #print()
            h.create_dataset(k, data=np.array(v_value, dtype='S'),compression = 'gzip')
            h[k].attrs['Units'] = v_attr

def merge_data(data_list):

    """Merge dictionaries with data.

    Keyword arguments:
    data_list -- the dictionary with data dictionaries
    """

    data = None

    for f in data_list:
        if not data:
            data = data_list[f]
        else:
            for key in data_list[f]:
                data[key] = np.append(data[key], data_list[f][key], axis=0)


    return data

def load(filename):

    """Load hdf5 file to data dictionary and return it.

    Keyword arguments:
    filename -- the full path to hdf5 file
    """

    with h5py.File(filename, 'r') as f:

        data = {}

        for key in f:
            data[key] = f[key][...]

    return data

def save(filename, data):

    """Create hdf5 file with given data.

    Keyword arguments:
    filename -- the full path to hdf5 file
    data -- dictionary with data
    """

    with h5py.File(filename, 'w') as f:

        for key in data:
            f.create_dataset(key, data[key].shape, dtype=data[key].dtype,compression='gzip')[...] = data[key]

## parallel worker to run vplanet ##
def par_worker(checkpoint_file,system_name,body_names,logfile,quiet,lock):

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

        os.chdir(folder)

        lock.acquire()
        datalist = []

        with open(checkpoint_file, 'r') as f:
            for newline in f:
                datalist.append(newline.strip().split())

        single_folder = folder.split('/')[-1]
        HDF5_File = single_folder + '.hdf5'

        if os.path.isfile(HDF5_File) == False:

            CreateHDF5(data, system_name, body_names, logfile, quiet, HDF5_File)
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

        os.chdir("../../")

def CreateMasterHDF5(folder_name, sims):
    master_file = folder_name + '.hdf5'
    filelist = []
    for i in sims:
        single_folder = i.split('/')[-1]
        HDF5_File = single_folder + '.hdf5'
        HDF5_path = i + '/' + HDF5_File
        filelist.append(HDF5_path)

    #
    # d_struct = {}
    # for i in filelist:
    #     f = h5py.File(i,"r+")
    #     d_struct[i] = f.keys()
    #     f.close()
    #
    # for i in filelist:
    #     for j in d_struct[i]:
    #         sub.call('h5copy','-i',i,'-o',master_file, '-s', j, '-d', j)
    #

    data = OrderedDict()

    for f in filelist:
        data[f] = load(f)

    save(master_file, merge_data(data))

    i = filelist[0]

    with h5py.File(i,'r') as filename:
        with h5py.File(master_file,'r+') as master_W:
            for k in filename.keys():
                units = filename[k].attrs.get('Units')
                master_W[k].attrs['Units'] = units

    for i in filelist:
        sub.run(['rm', i])
    sub.run(['rm','.' + folder_name + '_hdf5'])

def main():
    max_cores = mp.cpu_count()
    parser = argparse.ArgumentParser(description="Extract data from Vplanet simulations")
    parser.add_argument("InputFile", help="Name of the vspace input file")
    parser.add_argument("-c","--cores", type=int, default=max_cores, help="Number of processors used")
    parser.add_argument("-q","--quiet", action="store_true", help="no output for bigplanet")
    parser.add_argument("-m","--email",type=str, help="Mails user when bigplanet is complete")

    args = parser.parse_args()

    parallel_run_planet(args.InputFile, args.cores, args.quiet,args.email)

if __name__ == "__main__":

    main()
