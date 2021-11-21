#!/usr/bin/env python

import os
import pandas as pd
import numpy as np
import h5py


def ProcessLogFile(logfile, data, folder, verbose, incl=None, excl=None):
    prop = ''
    body = 'system'
    path = os.path.join(folder, logfile)
    if verbose == True:
        print(path)
    with open(path, 'r+', errors='ignore') as log:
        content = [line.strip() for line in log.readlines()]

    for line in content:

        if len(line) == 0:
            continue

        # First we need to get the body names and if its a inital or final value
        if line.startswith('-'):
            tmp_line = line.replace(
                '-', '').replace(':', '').strip().replace(' ', '_')

            if tmp_line.startswith('INITIAL_SYSTEM_PROPERTIES'):
                prop = 'initial'

            if tmp_line.startswith('FINAL_SYSTEM_PROPERTIES'):
                prop = 'final'
                body = 'system'

            if tmp_line.startswith('BODY'):
                body = tmp_line[tmp_line.find('_')+1:].strip()

            continue

        # if the line starts with a '(' that means its a variable we need to grab the units
        if line.startswith('('):
            fv_param = line[1:line.find(')')].strip()
            units = line[line.find('[')+1:line.find(']')].strip()

            if not units:
                units = 'nd'

            fv_value = line[line.find(':')+1:].strip()
            key_name = body + ':' + fv_param + ':' + prop

            # make this into a function
            if incl is not None:
                for i in incl:
                    if key_name == i:
                        # make this into a function
                        if key_name in data:
                            data[key_name].append(fv_value)
                        else:
                            data[key_name] = [units, fv_value]
                    else:
                        continue
            else:
                if key_name in data:
                    data[key_name].append(fv_value)
                else:
                    data[key_name] = [units, fv_value]

        # if the name starts with output order then its a list of variables
        if line.startswith('Output Order') and len(line[line.find(':'):]) > 1:
            parm_key = line[:line.find(':')].replace(' ', '')
            params = line[line.find(':') + 1:].strip().split(']')
            key_name = body + ':' + parm_key
            out_params = []

            for i in params:
                var = i[:i.find('[')].strip()
                units = i[i.find('[') + 1:]

                if not units:
                    units = 'nd'

                if var == '':
                    continue

                out_params.append([var, units])

                key_name_forward = body + ':' + var + ':forward'

                # make this into a function
                if incl is not None:
                    for j in incl:
                        if key_name_forward == j:
                            # make this into a function
                            if key_name_forward not in data:
                                data[key_name_forward] = [units]
                        else:
                            continue
                else:
                    if key_name_forward not in data:
                        data[key_name_forward] = [units]

            if incl is not None:
                for k in incl:
                    if key_name == k:
                        # make this into a function
                        if key_name not in data:
                            data[key_name] = out_params
                    else:
                        continue
            else:
                if key_name not in data:
                    data[key_name] = out_params

        # if the name starts with  grid output order then its a list of variables
        if line.startswith('Grid Output Order') and len(line[line.find(':'):]) > 1:
            parm_key = line[:line.find(':')].replace(' ', '')
            params = line[line.find(':') + 1:].strip().split(']')
            key_name = body + ':' + parm_key
            out_params = []

            for i in params:
                var = i[:i.find('[')].strip()
                units = i[i.find('[') + 1:]

                if not units:
                    units = 'nd'

                if var == '':
                    continue

                out_params.append([var, units])

                key_name_climate = body + ':' + var + ':climate'

                # make this into a function
                if incl is not None:
                    for j in incl:
                        if key_name_climate == j:
                            # make this into a function
                            if key_name_climate not in data:
                                data[key_name_climate] = [units]
                else:
                    if key_name_climate not in data:
                        data[key_name_climate] = [units]

            if incl is not None:
                for k in incl:
                    if key_name == k:
                        # make this into a function
                        if key_name not in data:
                            data[key_name] = out_params
                    else:
                        continue
            else:
                if key_name not in data:
                    data[key_name] = out_params

    return data


def ProcessOutputfile(file, data, body, Output, prefix, folder, verbose, incl=None, excl=None):

    path = os.path.join(folder, file)
    if verbose == True:
        print(path)

    header = []
    units = []
    for k, v in Output.items():
        for num in v:
            header.append(num[0])
            if num[1] == '':
                units.append('nd')
            else:
                units.append(num[1])

    sorted = pd.read_csv(path, header=None, delim_whitespace=True)
    sorted = sorted.to_numpy().transpose().tolist()

    for i, row in enumerate(sorted):
        key_name = body + ':' + header[i] + prefix

        # if key_name in data:
        #     data[key_name].append(row)
        # else:
        #     data[key_name] = [row]

        # make this into a function
        if incl is not None:
            for j in incl:
                if key_name == j:
                    # make this into a function
                    if key_name in data:
                        data[key_name].append(row)
                    else:
                        data[key_name] = [units[i], row]

                else:
                    continue
        else:
            if key_name in data:
                data[key_name].append(row)
            else:
                data[key_name] = [units[i], row]

    return data


def ProcessSeasonalClimatefile(prefix, data, body, name, folder, verbose, incl=None, excl=None):
    file_name = prefix + '.' + name + '.0'
    path = os.path.join(folder, "SeasonalClimateFiles/", file_name)

    if verbose == True:
        print(path)

    sorted = pd.read_csv(path, header=None, delim_whitespace=True).to_numpy()
    sorted = sorted.transpose().tolist()

    key_name = body + ':' + name
    units = ''
    if (name == 'DailyInsol' or name == 'SeasonalFIn' or
            name == 'SeasonalFOut' or name == 'SeasonalDivF'):
        units = 'W/m^2'
    if name == 'PlanckB':
        units = 'W/m^2/K'
    if name == 'SeasonalIceBalance':
        units = 'kg/m^2/s'
    if name == 'SeasonalTemp':
        units = 'deg C'
    if name == 'SeasonalFMerid':
        units = 'W'

    # if key_name not in data:
    #     data[key_name]= [units, sorted]
    # else:
    #     data[key_name].append(sorted)

    if incl is not None:
        for i in incl:
            if key_name == i:
                # make this into a function
                if key_name in data:
                    data[key_name].append(sorted)
                else:
                    data[key_name] = [units, sorted]
            else:
                continue
    else:
        if key_name in data:
            data[key_name].append(sorted)
        else:
            data[key_name] = [units, sorted]

    return data


def ProcessInputfile(data, in_file, folder, vplanet_help, verbose, incl=None, excl=None):

    # set the body name equal to the infile name
    body = in_file.partition('.')[0]
    path = os.path.join(folder, in_file)
    if verbose == True:
        print(path)
    # open the input file and read it into an array
    with open(path, "r") as file:

        content = [line.strip() for line in file.readlines()]

    # for every line in the array check if the line is blank
    # or if the line starts with a #
    next = False
    t_line = ''
    for num, line in enumerate(content):
        if len(line) == 0 or line.startswith('#'):
            continue

        # if theres a comment in the line we don't want that, so partition the
        # string and use everything before it
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
        value = line[1]

        key = key.replace('-', '')
        key_name = body + ':' + key + ':option'

        units = ProcessInfileUnits(key, value, folder, path, vplanet_help)

        if 'saOutputOrder' in key_name or 'saGridOutput' in key_name:
            for i in value:
                if value[0] == '-':
                    value = value[1:]

        # make this into a function
        if incl is not None:
            for i in incl:
                if key_name == i:
                    # make this into a function
                    if key_name in data:
                        data[key_name].append(value)
                    else:
                        data[key_name] = [units, value]
                else:
                    continue
        else:
            if key_name in data:
                data[key_name].append(value)
            else:
                data[key_name] = [units, value]

    return data


def ProcessInfileUnits(name, value, folder, in_file, vplanet_help):
    # check if the value is negative and has a negative option
    custom_unit = vplanet_help.get(name, {}).get('Custom Units')
    if '-' in value and custom_unit != None:
        unit = custom_unit
        return unit
    else:
        dim = vplanet_help.get(name, {}).get('Dimension')

        # since pressure and energy arent sUnits, we have to replace them with the dims for each
        if dim == None or dim == 'nd':
            unit = 'nd'
            return unit

        if 'pressure' in dim:
            dim = dim.replace('pressure', '(mass*length^-1*time^-2)')
        if 'energy' in dim:
            dim = dim.replace('energy', '(mass*length^2*time^-2)')

        # check the options file the value was in and see if the Dimension is there
        with open(in_file, 'r+') as infile:
            infile_lines = infile.readlines()

        for infile_line in infile_lines:
            if 'sUnitLength' in infile_line and 'length' in dim:
                dim = dim.replace('length', infile_line.split()[1])
            if 'sUnitAngle' in infile_line and 'angle' in dim:
                dim = dim.replace('angle', infile_line.split()[1])
            if 'sUnitTemp' in infile_line and 'temperature' in dim:
                dim = dim.replace('temperature', infile_line.split()[1])
            if 'sUnitMass' in infile_line and 'mass' in dim:
                dim = dim.replace('mass', infile_line.split()[1])
            if 'sUnitTime' in infile_line and 'time' in dim:
                dim = dim.replace('time', infile_line.split()[1])

            if infile_line == infile_lines[-1]:
                # if its not in the options file, it might be in in the vpl.in file
                with open(os.path.join(folder, 'vpl.in'), 'r+') as vplfile:
                    vpl_lines = vplfile.readlines()

                for vpl_line in vpl_lines:
                    if 'sUnitLength' in vpl_line and 'length' in dim:
                        dim = dim.replace('length', vpl_line.split()[1])
                    if 'sUnitAngle' in vpl_line and 'angle' in dim:
                        dim = dim.replace('angle', vpl_line.split()[1])
                    if 'sUnitTemp' in vpl_line and 'temperature' in dim:
                        dim = dim.replace('temperature', vpl_line.split()[1])
                    if 'sUnitMass' in vpl_line and 'mass' in dim:
                        dim = dim.replace('mass', vpl_line.split()[1])
                    if 'sUnitTime' in vpl_line and 'time' in dim:
                        dim = dim.replace('time', vpl_line.split()[1])

                # the only place left is the default of sUnit of the Dimension
                if vpl_line == vpl_lines[-1]:
                    if 'length' in dim:
                        dim = dim.replace(
                            'length', vplanet_help['sUnitLength']['Default Value'])
                    if 'angle' in dim:
                        dim = dim.replace(
                            'angle', vplanet_help['sUnitAngle']['Default Value'])
                    if 'temperature' in dim:
                        dim = dim.replace(
                            'temperature', vplanet_help['sUnitTemp']['Default Value'])
                    if 'mass' in dim:
                        dim = dim.replace(
                            'mass', vplanet_help['sUnitMass']['Default Value'])
                    if 'time' in dim:
                        dim = dim.replace(
                            'time', vplanet_help['sUnitTime']['Default Value'])
        unit = dim
    return unit


def GatherData(data, system_name, body_names, logfile, in_files, vplanet_help, folder, verbose):
    """
    ....
    """

    # for each of the infiles, process the data
    for infile in in_files:
        data = ProcessInputfile(data, infile, folder, vplanet_help, verbose)
    # first process the log file
    # gets the absoulte path for the log file
    data = ProcessLogFile(logfile, data, folder, verbose)
    # for each of the body names in the body_list
    # check and see if they have a grid
    # if so, then process those particular files
    for body in body_names:
        outputorder = body + ":OutputOrder"
        gridoutputorder = body + ":GridOutputOrder"
        # if output order from the log file isn't empty process it
        if outputorder in data:
            #OutputOrder = data[outputorder]
            OutputOrder = {}
            OutputOrder[outputorder] = data[outputorder]

            Outfile = body + ":sOutFile:option"
            if Outfile in data:
                file_name = data[Outfile]
            else:
                # need to figure out if its forward file or backwards file
                forwardOption = in_files[-1].partition(
                    '.')[0] + ":bDoForward:option"
                backwardOption = in_files[-1].partition(
                    '.')[0] + ":bDoBackward:option"
                if forwardOption in data:
                    file_name = system_name + '.' + body + '.forward'
                    prefix = ":forward"
                elif backwardOption in data:
                    file_name = system_name + '.' + body + '.backward'
                    prefix = ":backward"

            data = ProcessOutputfile(
                file_name, data, body, OutputOrder, prefix, folder, verbose)

        # now process the grid output order (if it exists)
        if gridoutputorder in data:
            GridOutputOrder = {}
            GridOutputOrder[gridoutputorder] = data[gridoutputorder]
            climate_name = system_name + '.' + body + '.Climate'
            data = ProcessOutputfile(
                climate_name, data, body, GridOutputOrder, ':climate', folder, verbose)
            prefix = system_name + '.' + body
            name = ['DailyInsol', 'PlanckB', 'SeasonalDivF', 'SeasonalFIn',
                    'SeasonalFMerid', 'SeasonalFOut', 'SeasonalIceBalance',
                    'SeasonalTemp']
            for i in range(len(name)):
                data = ProcessSeasonalClimatefile(
                    prefix, data, body, name[i], folder, verbose)

    return data


def DictToBP(data, vplanet_help, h5_file, verbose=False, group_name="", archive=True):

    for k, v in data.items():

        var = k.split(":")[1]
        end = k.split(':')[-1]

        if "OutputOrder" in var or "GridOutput" in var:
            v_value = v
            v_attr = ''

        else:
            v_attr = v[0]
            v_value = v[1:]

        if "Output" in var:
            tp = "S"

        elif var not in vplanet_help:
            tp = "float"

        else:
            if vplanet_help.get(var, {}).get('Type') == 'String' or vplanet_help.get(var, {}).get('Type') == 'String-Array':
                tp = "S"
            else:
                tp = "float"

        if archive == True and group_name:
            dataset_name = group_name + '/' + k
        else:
            dataset_name = k

        if verbose == True:
            print()
            print("Dataset:", dataset_name)
            print("Type:", tp)
            print("Units:", v_attr)
            print("Value:", v_value)
            print()

        h5_file.create_dataset(dataset_name, data=v_value,
                               compression='gzip', fletcher32=True)

        h5_file[dataset_name].attrs['Units'] = v_attr
