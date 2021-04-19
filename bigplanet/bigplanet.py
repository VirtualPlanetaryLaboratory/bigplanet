#!/usr/bin/env python

import os
import multiprocessing as mp
import subprocess as sub
import argparse
import h5py
import numpy as np
import csv


def GetDir(vspace_file):
    """ Give it input file and returns name of folder where simulations are located. """

    infiles = []
    # gets the folder name with all the sims
    with open(vspace_file, 'r') as vpl:
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

def GetSNames(in_files,sims):
    #get system and the body names
    body_names = []

    for file in in_files:
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
        else:
            with open(full_path, 'r') as infile:
                content = [line.strip().split() for line in infile.readlines()]
                for line in content:
                    if line:
                        if line[0] == 'sName':
                            body_names.append(line[1])

    return system_name,body_names

def GetVplanetHelp():
    #run vplanet -H and maybe format it to be saved as a dict?
    #that would be faster to search through for later
    vplanet_dict = {}

    with open('vplanet_help.txt','r+') as f:
        sub.call(['vplanet', '-H'],stdout = f)
        input = f.readlines()[43:]


    for line in input:

        if line.startswith('b') or line.startswith('d') or line.startswith('i') or line.startswith('s'):
            continue


        #we don't care about the dividers either
        if '=' in line:
            continue



        # we don't need any of the Output options so when we find it we gtfo
        if 'Output Parameters' in line:
            break



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

def ProcessOutputfile(climatefile, data, body, Output, prefix):

    header = []

    for i in Output:
        header.append([i][0][0])

    sorted = np.loadtxt(climatefile, unpack=True, dtype=str,encoding=None)

    for i,row in enumerate(sorted):
        key_name = body + '_' + header[i] + prefix
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

def ProcessInputfile(data,in_file):

    #set the body name equal to the infile name
    body = in_file.partition('.')[0]

    #open the input file and read it into an array
    with open(in_file,"r") as infile:

        content = [line.strip() for line in infile.readlines()]

    # for every line in the array check if the line is blank
    # or if the line starts with a #
    next = False
    for num,line in enumerate(content):
        if len(line) == 0 or line.startswith('#'):
            continue

        #if theres a comment in the line we don't want that, so partition the
        #string and use everything before it
        if '#' in line:
            line = line.partition('#')[0]
        if next == True:
                next = False
                continue
        # if there's a $ we need to get the next line and append it
        if '$' in line:
            next = True
            line = line.partition('$')[0]
            line += content[num + 1]
            if '-' in line:
                 line = line.replace('-', '')

        line = line.split()
        #print(line)
        key = line[0]
        value = line[1:]

        key_name = body + '_' + key + '_option'
        units = ''
        #units = ProcessOptionUnits(key,value,vplanet_help)

        #print("Key:",key_name)
        #print("Value:",value)

    if key_name in data:
        data[key_name].append(value)

    else:
        data[key_name] = [units, value]

    return data

def ProcessInfileUnits(name,value,vpl_file,vplanet_help):
    # find the table in vplanet -h with the name we want
    #if there is a minus sign check and see what the custom units are
    #if not a minus, check the vpl file to see if the user set any particular units
    #if thats not true, then use the default i guess
    print()


def CreateHDF5Group(data, system_name, body_names, logfile, group_name, in_files, h5_file):
    """
    ....
    """

    #for each of the infiles, process the data
    for infile in in_files:
        data = ProcessInputfile(data,infile)

    # first process the log file
    data = ProcessLogFile(logfile, data)
    # for each of the body names in the body_list
    # check and see if they have a grid
    # if so, then process those particular files
    for body in body_names:
        outputorder = body + "_OutputOrder"
        gridoutputorder = body + "_GridOutputOrder"
        # if output order from the log file isn't empty process it
        if outputorder in data:
            OutputOrder = data[outputorder]
            forward_name = system_name + '.' + body + '.forward'
            data = ProcessOutputfile(forward_name, data, body, OutputOrder,'_forward')

        #now process the grid output order (if it exists)
        if gridoutputorder in data:
            GridOutputOrder = data[gridoutputorder]
            climate_name = system_name + '.' + body + '.Climate'
            data = ProcessOutputfile(climate_name, data, body, GridOutputOrder,'_climate')
            prefix = system_name + '.' + body
            name = ['DailyInsol','PlanckB','SeasonalDivF','SeasonalFIn',
                    'SeasonalFMerid','SeasonalFOut','SeasonalIceBalance',
                    'SeasonalTemp']
            for i in range(len(name)):
                data = ProcessSeasonalClimatefile(prefix,data,body,name[i])

    # now create the group where the data is stored in the HDF5 file
    for k, v in data.items():
        if len(v) == 2:
            v_attr = v[0]
            v_value = [v[1]]
        else:
            v_value = v[0]
            v_attr = ''

        dataset_name = group_name + '/'+ k


        h5_file.create_dataset(dataset_name, data=np.array(v_value, dtype='S'), compression = 'gzip')
        h5_file[dataset_name].attrs['Units'] = v_attr

def CreateCP(checkpoint_file,input_file,sims):
    with open(checkpoint_file,'w') as cp:
        cp.write('Vspace File: ' + os.getcwd() + '/' + input_file + '\n')
        cp.write('Total Number of Simulations: '+ str(len(sims)) + '\n')
        for f in range(len(sims)):
            cp.write(sims[f] + " " + "-1 \n")
        cp.write('THE END \n')

def ReCreateCP(checkpoint_file,input_file,quiet,sims,folder_name,email):

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

    if all(l[1] == '1' for l in datalist[2:-2]) == True:
        print("All Groups in BPL file exist")

        if email is not None:
             SendMail(email, folder_name)
        exit()

    else:
        if not quiet:
            print('Continuing from Checkpoint...')



def Main(vspace_file,cores,quiet,email,parallel):
    # Get the directory and list of  from the vspace file
    dest_folder, infile_list = GetDir(vspace_file)

    # Get the list of simulation (trial) names in a List
    sim_list = GetSims(dest_folder)

    # Get the SNames (sName and sSystemName) for the simuations
    # Save the name of the log file
    system_name, body_list = GetSNames(infile_list,sim_list)
    log_file = system_name + ".log"

    #creates the chepoint file name
    checkpoint_file = os.getcwd() + '/' + '.' + dest_folder + '_BPL'

    # Create the checkpoint file to be used to keep track of the groups
    if os.path.isfile(checkpoint_file) == False:
        CreateCP(checkpoint_file,vspace_file,sim_list)

    #if it does exist, it checks for any 0's (sims that didn't complete) and
    #changes them to -1 to be re-ran
    else:
        ReCreateCP(checkpoint_file,vspace_file,quiet,sim_list,dest_folder,email)

    # now that we have everything we need
    # we save the name of the Master HDF5 file
    master_hdf5_file = dest_folder + '.bpl'


    if parallel:
        #creates the lock and workers for the parallel processes
        lock = mp.Lock()
        workers = []

        #for each core, create a process that adds a group to the hdf5 file and adds that to the Master HDF5 file
        with h5py.File(master_hdf5_file, 'w') as Master:
            for i in range(cores):
                workers.append(mp.Process(target=par_worker,
                               args=(checkpoint_file, system_name, body_list, log_file, infile_list, quiet, lock, Master)))
            for w in workers:
                w.start()
            for w in workers:
                w.join()

        sub.run(['rm',checkpoint_file])

    else:
        # loop over every trial in the list of simulations
        # for each trial we need to create a group that hold the various files we
        # want to populate the HDF5 file with
        with h5py.File(master_hdf5_file, 'w') as Master:
            for trial in sim_list:
                data = {}
                group_name = trial.split('/')[-1]
                os.chdir(trial)
                CreateHDF5Group(data, system_name, body_list, log_file, group_name,infile_list, Master)
                os.chdir('../../')

def par_worker(checkpoint_file,system_name,body_list,log_file,in_files,quiet,lock,h5_file):

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

        group_name = folder.split('/')[-1]

        if group_name not in h5_file:
            CreateHDF5Group(data, system_name, body_list, log_file, group_name,in_files, h5_file)
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

def Arguments():
    max_cores = mp.cpu_count()
    parser = argparse.ArgumentParser(description="Extract data from Vplanet simulations")
    parser.add_argument("vspace_file", help="Name of the vspace input file")
    parser.add_argument("-c","--cores", type=int, default=max_cores, help="Number of processors used")
    parser.add_argument("-q","--quiet", action="store_true", help="no output for bigplanet")
    parser.add_argument("-m","--email",type=str, help="Mails user when bigplanet is complete")
    parser.add_argument("-p","--parallel",action="store_true", help="parallel run of bigplanet")

    args = parser.parse_args()

    Main(args.vspace_file,args.cores,args.quiet,args.email,args.parallel)


if __name__ == "__main__":
    Arguments()
