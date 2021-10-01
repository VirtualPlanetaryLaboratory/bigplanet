#!/usr/bin/env python


import multiprocessing as mp
import h5py
import numpy as np
from scipy import stats
from .bp_get import GetVplanetHelp
from .bp_process import CreateHDF5Group


def BPLFile(hf):
    return h5py.File(hf,'r')


def ExtractColumn(hf,k):
    """
    Returns all the data for a single key (column) in a given HDF5 file.

    Parameters
    ----------
    hf : File
        The HDF5 where the data is stored.
        Example:
            HDF5_File = h5py.File(filename, 'r')
    k : str
        the name of the column that is to be extracted
        Example:
            k = 'earth_Obliquity_final'
        The syntax of the column names is body_variable_aggregation
        the lists of aggregations (and how to call them) is as follows:

            forward file data (forward), initial data (initial),
            final data (final), Output Order List (OutputOrder)

            Note: The following statistics only will work with forward data
            mean (mean), mode (mode), standard deviation (stddev),
            min (min), max (max), gemoetric mean (geomean)

    Returns
    -------
    data : np.array
        A numpy array of the column of table of values


    """
    data = []
    archive = False
    key_list = list(hf.keys())


    if ":" not in key_list:
        print("this is a test")
        archive = True



    print(archive)
    var = k.split(":")[1]

    if var == 'OutputOrder' or var == 'GridOutputOrder':
        if archive == True:
            dataset = hf[key_list[0] + '/' + k]
            for d in dataset:
                for value in d:
                    data.append(value)
        else:
            for v in hf[k]:
                for item in v:
                    data.append(item)

    else:
        aggreg = k.split(":")[2]

        if aggreg == 'forward':
            if archive == True:
                for key in key_list:
                    dataset = hf[key + '/' + k]
                    data.append(HFD5Decoder(hf,dataset))
            else:
                 for v in hf[k]:
                    for item in v:
                        data.append(item)

        elif aggreg == 'mean':
            argument = ForwardData(hf,k)
            for i in argument:
                data.append((np.mean(i, axis = 1)))

        elif aggreg == 'stddev':
            argument = ForwardData(hf,k)
            for i in argument:
                data.append((np.std(i, axis = 1)))

        elif aggreg == 'min':
            argument = ForwardData(hf,k)
            for i in argument:
                data.append((np.amin(i, axis = 1)))

        elif aggreg == 'max':
            argument = ForwardData(hf,k)
            for i in argument:
                data.append((np.amax(i,axis = 1)))

        elif aggreg == 'mode':
            argument = ForwardData(hf,k)
            for i in argument:
                data.append((stats.mode(i, axis = 1)))

        elif aggreg == 'geomean':
            argument = ForwardData(hf,k)
            for i in argument:
                data.append((stats.gmean(i, axis = 1)))

        elif aggreg == 'initial' or aggreg == 'final' or aggreg == 'option':
            if archive == True:
                for key in key_list:
                    dataset = hf[key + '/' + k]
                    for d in dataset:
                        d = d.astype(float,casting = 'safe')
                        data.append(d)
            else:
                dataset = hf[k]
                for d in dataset:
                    d = d.astype(float,casting = 'safe')
                    data.append(d)

        else:
            print('ERROR: Uknown aggregation option: ', aggreg)
            exit()
    return data


def ExtractUnits(hf,k):
    """
    Returns all the data for a single key (column) in a given HDF5 file.

    Parameters
    ----------
    hf : File
        The HDF5 where the data is stored.
        Example:
            HDF5_File = h5py.File(filename, 'r')
    k : str
        the name of the column that is to be extracted
        Example:
            k = 'earth_Obliquity_final'
        The syntax of the column names is body_variable_aggregation
        the lists of aggregations (and how to call them) is as follows:

            forward file data (forward), initial data (initial),
            final data (final), Output Order List (OutputOrder)

            Note: The following statistics only will work with forward data
            mean (mean), mode (mode), standard deviation (stddev),
            min (min), max (max), gemoetric mean (geomean)

    Returns
    -------
    units : string
        A string value of the units
    """
    if ":" not in hf.keys():
        key_list = list(hf.keys())
        dataset = hf[key_list[0] + '/' + k]
    else:
        dataset = hf[k]
    return dataset.attrs.get('Units')

def ForwardData(hf,k):
    data = []
    forward = k.rpartition(':')[0] + ':forward'
    if ":" not in hf.keys():
        key_list = list(hf.keys())
        for key in key_list:
            dataset = hf[key + '/' + forward]
            data.append(HFD5Decoder(dataset))
    else:
         dataset = hf[forward]
         data.append(HFD5Decoder(dataset))
    return data

def HFD5Decoder(dataset):
    #because the data is saved as a UTF-8 string, we need to decode it and
    #turn it into a
    data = []
    for d in dataset:
        if "forward" in dataset.name:
            for value in d:
                value = value.astype(float, casting = 'safe')
                data.append(value)
        else:
            d = d.astype(float,casting = 'safe')
            data.append(d)
    #and now we reshape it the same shape as the original dataset
    shape = dataset.shape
    data = np.reshape(data,shape)

    return data

def WriteOutput(inputfile, columns,exportfile="bigplanet.out",delim=" ",header=False,ulysses=False):
    """
    Writes an Output file in csv format

    Parameters
    ----------
    input file : HDF5 file
        the HDF5 file where the data is stored
        Example:
            HDF5_File = h5py.File(filename, 'r')
    columns : list of strings
        a list of variables that are to be written to the csv file
        Example:
            columns = ['earth_Obliquity_final','earth_Instellation_final']
    file : string
        the name of the output file
        Default is Bigplanet.out
        Example:
            file="bigplanet.out"
    delim : string
        the delimiter for the output file
        Example:
            delim = ","
    header : boolean
        if True, headers are put on the first line of the output
        Default is False
    ulysses : boolean
        True/False boolean determing if the output file will be in VR Ulysses format
        If True, the output file will have headers, and be named 'User.csv'
    """
    export = []
    units = []
    for i in columns:
        export.append(ExtractColumn(inputfile,i))
        units.append(ExtractUnits(inputfile,i))

    if ".bpl" in exportfile:
        for j,value in enumerate(columns):
            with h5py.File(exportfile,"w") as f_dest:
                f_dest.create_dataset(value, data=export[j], compression = 'gzip')
                f_dest[value].attrs['Units'] = units[j]
        print("Done")
    else:

        if ulysses == True:
            delim = ','
            header = True
            exportfile = 'User.csv'

        if delim == "":
            print('ERROR: Delimiter cannot be empty')
            exit()

        with open(exportfile, "w", newline="") as f:
            if header == True:
                for count,i in enumerate(columns):
                    f.write(i + '[' + units[count] + ']')
                    if columns[-1] != i:
                        f.write(delim)

                f.write("\n")

            icol, irow = export.shape
            for i in range(irow):
                for j in range(icol):
                    f.write(str(export[j][i]))
                    if j < icol - 1:
                        f.write(delim)
                f.write("\n")
