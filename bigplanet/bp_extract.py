#!/usr/bin/env python


import multiprocessing as mp
import h5py
import numpy as np
from scipy import stats
import statistics as st
import csv

from .bp_get import GetVplanetHelp
from .bp_process import DictToBP


def BPLFile(hf):
    return h5py.File(hf, 'r')


def ExtractColumn(hf, k):
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

    if ":" not in key_list[0]:
        archive = True

    var = k.split(":")[1]

    if var == 'OutputOrder' or var == 'GridOutputOrder':
        if archive == True:
            dataset = hf[key_list[0] + '/' + k]
            for d in dataset:
                for value in d:
                    value = value.astype(str, casting='safe')
                    data.append(value)
        else:
            for v in hf[k]:
                for item in v:
                    item = item.astype(str, casting='safe')
                    data.append(item)

    else:
        aggreg = k.split(":")[2]

        if aggreg == 'forward':
            if archive == True:
                for key in key_list:
                    dataset = hf[key + '/' + k]
                    data.append(HFD5Decoder(dataset))
            else:
                for v in hf[k]:
                    for item in v:
                        data.append(item)

        elif aggreg == 'mean':
            argument = ForwardData(hf, k)
            for i in argument:
                data.append((st.mean(i)))

        elif aggreg == 'stddev':
            argument = ForwardData(hf, k)
            for i in argument:
                data.append((st.stdev(i)))

        elif aggreg == 'min':
            argument = ForwardData(hf, k)
            for i in argument:
                data.append((min(i)))

        elif aggreg == 'max':
            argument = ForwardData(hf, k)
            for i in argument:
                data.append((max(i)))

        elif aggreg == 'mode':
            argument = ForwardData(hf, k)
            for i in argument:
                data.append((stats.mode(i)))

        elif aggreg == 'geomean':
            argument = ForwardData(hf, k)
            for i in argument:
                data.append((stats.gmean(i)))

        elif aggreg == 'initial' or aggreg == 'final' or aggreg == 'option':
            if archive == True:
                for key in key_list:
                    dataset = hf[key + '/' + k]
                    for d in dataset:
                        d = d.astype(float, casting='safe')
                        data.append(d)
            else:
                for d in hf[k]:
                    for v in d:
                        v = v.astype(float, casting='safe')
                        data.append(v)

        else:
            print('ERROR: Uknown aggregation option: ', aggreg)
            exit()
    return data


def ExtractUnits(hf, k):
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
    key_list = list(hf.keys())

    if ":" not in key_list[0]:
        dataset = hf[key_list[0] + '/' + k]
    else:
        dataset = hf[k]
    return dataset.attrs.get('Units')


def ForwardData(hf, k):
    data = []
    key_list = list(hf.keys())
    forward = k.rpartition(':')[0] + ':forward'
    if ":" not in key_list[0]:
        for key in key_list:
            dataset = hf[key + '/' + forward]
            for d in dataset:
                for v in d:
                    data.append(v)
    else:
        dataset = hf[forward]
        for d in dataset:
            data.append(d)
    return data


def HFD5Decoder(dataset):
    # because the data is saved as a UTF-8 string, we need to decode it and
    # turn it into a
    for d in dataset:
        if "forward" in dataset.name:
            for value in d:
                value = value.astype(float, casting='safe')
                # data.append(value)
        else:
            d = d.astype(float, casting='safe')
            # data.append(d)
    # and now we reshape it the same shape as the original dataset
    #shape = dataset.shape
    #data = np.reshape(data, shape)
    # print(data)
    # data.tolist()

    return dataset


def ExtractUniqueValues(hf, k):
    """
    Extracts unique values from a key in an HDF5 file.
    Returns a numpy array of the dataset
    Parameters
    ----------
    HDF5 : File
        The HDF5 where the data is stored
        Example:
            HDF5_File = h5py.File(filename, 'r')
    key : str
        the name of the column that you want unique values from
        Example:
            key = 'earth_Obliquity_final'
    Returns
    -------
    unique : np.array
        A numpy array of the unique values in key
    """
    key_list = list(hf.keys())
    data = []
    archive = False

    if ":" not in key_list[0]:
        archive = True

    var = k.split(":")[1]

    if archive == True:
        for key in key_list:
            dataset = hf[key + '/' + k]
            if len(dataset.shape) != 1:
                data = HFD5Decoder(hf, dataset)
                data.flatten()
            else:
                for d in dataset:
                    data.append(d)
    else:
        for d in hf[k]:
            for v in d:
                data.append(v)

    unique = np.unique(data)
    return unique


def CreateMatrix(xaxis, yaxis, zarray, orientation=1):
    """
    Creates a Matrix for Contour Plotting of Data. Run ExtractUniqueValue()
    prior to CreateMatrix() to get the ticks for the xaxis and yaxis
    Parameters
    ----------
    xaxis : nump array
        the numpy array of unique values of the xaxis
        Example:
            xasis = ExtractUniqueValues(data,'earth_Obliquity_forward')
    yaxis : numpy array
        the numpy array of unique values of the xaxis
        Example:
            yaxis = ExtractUniqueValues(data,'earth_Instellation_final')
    zarray : numpy array
        the numpy array of the values of z for Contour Plotting
        Example:
            zarray = ExtractColumn(data,'earth_IceBeltLand_final')
    Returns
    -------
    zmatrix : numpy array
        zarray in the shape of (xaxis,yaxis)
    """

    xnum = len(xaxis)
    ynum = len(yaxis)

    if xnum * ynum != len(zarray):
        print("ERROR: Cannot reshape zarray into shape (", xnum, ",", ynum, ")")
        exit()

    zmatrix = np.reshape(zarray, (ynum, xnum))
    zmatrix = np.flipud(zmatrix)

    for i in range(0, orientation):
        zmatrix = rotate90Clockwise(zmatrix)

    zmatrix = np.flipud(zmatrix)

    return zmatrix


def rotate90Clockwise(A):
    N = len(A[0])
    for i in range(N // 2):
        for j in range(i, N - i - 1):
            temp = A[i][j]
            A[i][j] = A[N - 1 - j][i]
            A[N - 1 - j][i] = A[N - 1 - i][N - 1 - j]
            A[N - 1 - i][N - 1 - j] = A[j][N - 1 - i]
            A[j][N - 1 - i] = temp

    return A


def ArchiveToFiltered(inputfile, columns, exportfile):
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
        export.append(ExtractColumn(inputfile, i))
        units.append(ExtractUnits(inputfile, i))

    if ".bpf" in exportfile:
        for j, value in enumerate(columns):
            with h5py.File(exportfile, "w") as f_dest:
                f_dest.create_dataset(
                    value, data=export[j], compression='gzip')
                f_dest[value].attrs['Units'] = units[j]


def ArchiveToCSV(inputfile, columns, exportfile, delim=" ", header=False, ulysses=0, group=None):
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
        if group == None:
            export.append(ExtractColumn(inputfile, i))
            units.append(ExtractUnits(inputfile, i))
        else:
            data = inputfile[group][i][0]
            for i in data:
                export.append(i)

    if ulysses == 1:
        delim = ','
        exportfile = 'User.csv'

    if delim == "":
        print('ERROR: Delimiter cannot be empty')
        exit()

    with open(exportfile, "w", newline="") as f:
        writer = csv.writer(f, delimiter=delim)
        if ulysses == 1:
            headers = []
            headers.append("")
            for i in columns:
                headers.append(i)
            writer.writerow(headers)

        if header == True:
            writer.writerow(columns)

        export = np.array(export, dtype='object').T.tolist()
        for name in export:
            for data in name:
                writer.writerow([data])


def DictToCSV(dictData, exportfile="bigplanet.csv", delim=" ", header=False, ulysses=0):
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

    if ulysses == 1:
        delim = ','
        exportfile = 'User.csv'

        if delim == "":
            print('ERROR: Delimiter cannot be empty')
            exit()

        with open(exportfile, "w", newline="") as f:
            writer = csv.DictWriter(f, dictData.keys(), delimiter=delim)

            if ulysses == 1:
                headers = []
                headers.append("")
                for i in dictData:
                    headers.append(i)
                writer.writerow(headers)

            if header == True:
                writer.writeheader()

            writer.writerow(dictData)