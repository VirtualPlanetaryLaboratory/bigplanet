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
    sims = sorted([f.path for f in os.scandir(os.path.abspath(folder_name)) if f.is_dir()])
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
    command = "vplanet -H | egrep -v '^$|^\+' | cut -f 2,4 -d '|' | egrep '^ \*\*|^ Cust|^ Type|^ Dim|^ Defa|^Output Parameters'"
    py_ver = sys.version.split()[0]
    print(py_ver)
    if '3.6' in py_ver:
        proc = sub.run(command, shell = True, universal_newlines = True, stdout=sub.PIPE,stderr=sub.PIPE)
    else:
        proc = sub.run(command, shell = True, text = True, stdout=sub.PIPE,stderr=sub.PIPE)
    output = proc.stdout.splitlines()

    vplanet_dict = {}

    for count, line in enumerate(output):
        if ((line.startswith(' **b') or line.startswith(' **d') or line.startswith(' **i') or line.startswith(' **s')) or line.startswith(' **sa') and len(line.split()) == 1):

            option = line.strip("** ")
            #print("Option:",option)
            vplanet_dict[option] = {}
            num = count + 1
            while num != count:
                if "Type" in output[num]:
                    tp = output[num].rpartition('|')[-1].strip()
                    vplanet_dict[option]['Type'] = tp
                    #print("Type:",tp)
                    num += 1

                elif "Custom unit" in output[num]:
                    custom_unit = output[num].rpartition('|')[-1].strip()
                    vplanet_dict[option]['Custom Unit'] = custom_unit
                    #print("Custom Unit:",custom_unit)
                    num += 1

                elif "Dimension(s)" in output[num]:
                    dim = output[num].rpartition('|')[-1].strip()
                    vplanet_dict[option]['Dimension'] = dim
                    #print("Dimension:",dim)
                    num += 1

                elif "Default value" in output[num]:
                    default = output[num].rpartition('|')[-1].strip()
                    vplanet_dict[option]['Default Value'] = default
                    #print("Default Value",default)
                    #print()

                    num += 1

                elif "**" in output[num]:
                    num = count

                else:
                    num += 1

        if "Output Parameters" in line:
            break

    return vplanet_dict



def ProcessLogFile(logfile, data,folder):
    prop = ''
    body = 'system'
    with open(os.path.join(folder,logfile), 'r') as log:
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

def ProcessOutputfile(file, data, body, Output, prefix, folder):

    path = os.path.join(folder,file)
    #print(path)
    header = []
    for i in Output:
        header.append([i][0][0])

    sorted = np.genfromtxt(path, dtype=float,encoding=None)
    sorted = sorted.transpose().tolist()

    for i,row in enumerate(sorted):
        key_name = body + '_' + header[i] + prefix
        data[key_name].append(row)

    return data

def ProcessSeasonalClimatefile(prefix, data, body, name,folder):
    file_name = prefix + '.' + name + '.0'
    path = os.path.join(folder,"SeasonalClimateFiles/", file_name)
    sorted = np.genfromtxt(path, dtype=float,encoding=None)
    sorted = sorted.tolist()

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
        data[key_name]= [units, sorted]
    else:
        data[key_name].append(sorted)

    return data

def ProcessInputfile(data,in_file, folder, vplanet_help):

    #set the body name equal to the infile name
    body = in_file.partition('.')[0]
    infile = os.path.join(folder,in_file)
    #open the input file and read it into an array
    with open(infile,"r") as file:

        content = [line.strip() for line in file.readlines()]

    # for every line in the array check if the line is blank
    # or if the line starts with a #
    next = False
    t_line = ''
    for num,line in enumerate(content):
        if len(line) == 0 or line.startswith('#'):
            continue

        #if theres a comment in the line we don't want that, so partition the
        #string and use everything before it
        if '#' in line:
            line = line.partition('#')[0]
        # if there's a $ we need to get the next line and append it
        if '$' in line:
            next = True
            line = line.partition('$')[0]
            t_line = t_line + line
            continue

        if next == True:
            next = False
            t_line = t_line + line
            line = t_line
            t_line = ''

        line = line.split()
        key = line[0]
        value = line[1:]


        key = key.replace('-','')
        key_name = body + '_' + key + '_option'

        units = ProcessInfileUnits(key, value, folder, infile, vplanet_help)

        if 'saOutputOrder' in key_name or 'saGridOutput' in key_name:
            value = [i.replace('-','') for i in value]

        if key_name in data:
            data[key_name].append(value)

        else:
            data[key_name] = [units, value]

    return data

def ProcessInfileUnits(name,value,folder,in_file, vplanet_help):
    # check if the value is negative and has a negative option
    custom_unit = vplanet_help.get(name,{}).get('Custom Units')
    if '-' in value and custom_unit != None:
        unit = custom_unit
        return unit
    else:
        dim = vplanet_help.get(name,{}).get('Dimension')

        #since pressure and energy arent sUnits, we have to replace them with the dims for each
        if dim == None or dim == 'nd':
            unit = 'nd'
            return unit

        if 'pressure' in dim:
            dim = dim.replace('pressure','(mass*length^-1*time^-2)')
        if 'energy' in dim:
            dim = dim.replace('energy','(mass*length^2*time^-2)')

        #check the options file the value was in and see if the Dimension is there
        with open(in_file, 'r+') as infile:
            infile_lines = infile.readlines()

        for infile_line in infile_lines:
            if 'sUnitLength' in infile_line and 'length' in dim:
                dim = dim.replace('length',infile_line.split()[1])
            if 'sUnitAngle' in infile_line and 'angle' in dim:
                dim = dim.replace('angle',infile_line.split()[1])
            if 'sUnitTemp' in infile_line and 'temperature' in dim:
                dim = dim.replace('temperature',infile_line.split()[1])
            if 'sUnitMass' in infile_line and 'mass' in dim:
                dim = dim.replace('mass',infile_line.split()[1])
            if 'sUnitTime' in infile_line and 'time' in dim:
                dim = dim.replace('time',infile_line.split()[1])

            if infile_line == infile_lines[-1]:
#if its not in the options file, it might be in in the vpl.in file
                with open(os.path.join(folder,'vpl.in'), 'r+') as vplfile:
                    vpl_lines = vplfile.readlines()

                for vpl_line in vpl_lines:
                    if 'sUnitLength' in vpl_line and 'length' in dim:
                        dim = dim.replace('length',vpl_line.split()[1])
                    if 'sUnitAngle' in vpl_line and 'angle' in dim:
                        dim = dim.replace('angle',vpl_line.split()[1])
                    if 'sUnitTemp' in vpl_line and 'temperature' in dim:
                        dim = dim.replace('temperature',vpl_line.split()[1])
                    if 'sUnitMass' in vpl_line and 'mass' in dim:
                        dim = dim.replace('mass',vpl_line.split()[1])
                    if 'sUnitTime' in vpl_line and 'time' in dim:
                        dim = dim.replace('time',vpl_line.split()[1])

#the only place left is the default of sUnit of the Dimension
                if vpl_line == vpl_lines[-1]:
                    if 'length' in dim:
                        dim = dim.replace('length',vplanet_help['sUnitLength']['Default Value'])
                        #dim = dim.replace('length',vplanet_help.get('sUnitLength',{}).get('Default Value'))
                    if 'angle' in dim:
                        dim = dim.replace('angle',vplanet_help['sUnitAngle']['Default Value'])
                        #dim = dim.replace('angle',vplanet_help.get('sUnitAngle',{}).get('Default Value'))
                    if 'temperature' in dim:
                        dim = dim.replace('temperature',vplanet_help['sUnitTemp']['Default Value'])
                        #dim = dim.replace('temperature',vplanet_help.get('sUnitTemp',{}).get('Default Value'))
                    if 'mass' in dim:
                        dim = dim.replace('mass',vplanet_help['sUnitMass']['Default Value'])
                        #dim = dim.replace('mass',vplanet_help.get('sUnitMass',{}).get('Default Value'))
                    if 'time' in dim:
                        dim = dim.replace('time',vplanet_help['sUnitTime']['Default Value'])
                        #dim = dim.replace('time',vplanet_help.get('sUnitTime',{}).get('Default Value'))
        unit = dim
    return unit



def CreateHDF5Group(data, system_name, body_names, logfile, group_name, in_files, vplanet_help, folder, h5_file):
    """
    ....
    """

    #for each of the infiles, process the data
    for infile in in_files:
        data = ProcessInputfile(data,infile,folder,vplanet_help)
    # first process the log file
    #gets the absoulte path for the log file
    data = ProcessLogFile(logfile, data, folder)
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
            data = ProcessOutputfile(forward_name, data, body, OutputOrder,'_forward',folder)

        #now process the grid output order (if it exists)
        if gridoutputorder in data:
            GridOutputOrder = data[gridoutputorder]
            climate_name = system_name + '.' + body + '.Climate'
            data = ProcessOutputfile(climate_name, data, body, GridOutputOrder,'_climate',folder)
            prefix = system_name + '.' + body
            name = ['DailyInsol','PlanckB','SeasonalDivF','SeasonalFIn',
                    'SeasonalFMerid','SeasonalFOut','SeasonalIceBalance',
                    'SeasonalTemp']
            for i in range(len(name)):
                data = ProcessSeasonalClimatefile(prefix,data,body,name[i],folder)

    # now create the group where the data is stored in the HDF5 file
    for k, v in data.items():
        if len(v) == 2:
            v_attr = v[0]
            v_value = v[1]
        else:
            v_value = v
            v_attr = ''

        var = k.split("_")[1]
        #print(var)

        if "OutputOrder" in var or "GridOutput" in var:
            tp = "S"

        elif var not in vplanet_help:
            tp = "float"
        else:
            if vplanet_help.get(var,{}).get('Type') == 'String' or vplanet_help.get(var,{}).get('Type') == 'String-Array':
                tp = "S"
            else:
                tp = "float"

        dataset_name = group_name + '/'+ k

        #print("Dataset:",dataset_name)
        #print("Type:",tp)
        #print("value:",v_value)

        h5_file.create_dataset(dataset_name, data=np.array([v_value] ,dtype = tp), compression = 'gzip')

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



def Main(vspace_file,cores,quiet,email):
    # Get the directory and list of  from the vspace file
    dest_folder, infile_list = GetDir(vspace_file)
    # Get the list of simulation (trial) names in a List
    sim_list = GetSims(dest_folder)
    # Get the SNames (sName and sSystemName) for the simuations
    # Save the name of the log file
    system_name, body_list = GetSNames(infile_list,sim_list)
    log_file = system_name + ".log"

    #gets the dictionary of input params
    vplanet_help = GetVplanetHelp()

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
    master_hdf5_file = os.path.abspath(dest_folder + '.bpl')

    #creates the lock and workers for the parallel processes
    lock = mp.Lock()
    workers = []

    #for each core, create a process that adds a group to the hdf5 file and adds that to the Master HDF5 file
    for i in range(cores):
        workers.append(mp.Process(target=par_worker,
                       args=(checkpoint_file, system_name, body_list, log_file, infile_list, quiet, lock, vplanet_help, master_hdf5_file)))
    for w in workers:
        w.start()
    for w in workers:
        w.join()

def par_worker(checkpoint_file,system_name,body_list,log_file,in_files,quiet,lock,vplanet_help, h5_file):

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

        #creates the bpl file and reads to make sure the group name is in the file
        with h5py.File(h5_file, 'a') as Master:
            #if not then add it
            if group_name not in Master:
                CreateHDF5Group(data, system_name, body_list, log_file, group_name, in_files, vplanet_help, folder, Master)

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


def Arguments():
    max_cores = mp.cpu_count()
    parser = argparse.ArgumentParser(description="Extract data from Vplanet simulations")
    parser.add_argument("vspace_file", help="Name of the vspace input file")
    parser.add_argument("-c","--cores", type=int, default=max_cores, help="Number of processors used")
    parser.add_argument("-q","--quiet", action="store_true", help="no output for bigplanet")
    parser.add_argument("-m","--email",type=str, help="Mails user when bigplanet is complete")
    args = parser.parse_args()

    Main(args.vspace_file,args.cores,args.quiet,args.email)


if __name__ == "__main__":
    Arguments()
