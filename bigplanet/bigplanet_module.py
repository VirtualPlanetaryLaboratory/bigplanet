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
Code for Bigplanet Module
"""

def HDF5File(hf):
    return h5py.File(hf,'r')

def PrintKeys(hf):
    """
    Print all the keys names in the HDF5 file

    Parameters
    ----------
    hf : File
        The HDF5 where the data is stored.
        Example:
            HDF5_File = h5py.File(filename, 'r')

    """

    for k in hf.keys():
        print("Key:", k)

        body = k.split("_")[0]
        variable = k.split("_")[1]

        if variable == "OutputOrder" or variable == "GridOutputOrder":
            continue
        else:
            aggregation = k.split("_")[2]

            if aggregation == 'forward' or aggregation =='climate':
                print("Key: " + body + '_'+ variable + '_min')
                print("Key: " + body + '_'+ variable + '_max')
                print("Key: " + body + '_'+ variable + '_mean')
                print("Key: " + body + '_'+ variable + '_mode')
                print("Key: " + body + '_'+ variable + '_geomean')
                print("Key: " + body + '_'+ variable + '_stddev')

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

    body = k.split("_")[0]
    var = k.split("_")[1]

    if var == 'OutputOrder' or var == 'GridOutputOrder':
        d = hf.get(k)
        data = [v.decode() for d in hf[k] for v in d]
        shape = hf[k].shape
        data = np.reshape(data,(shape))
    else:
        aggreg = k.split("_")[2]

        if aggreg == 'forward':
            d = hf.get(k)
            data = HFD5Decoder(hf,k)

        elif aggreg == 'mean':
            data = ArgumentParser(hf,k)
            data = np.mean(data, axis=1)

        elif aggreg == 'stddev':
            data = ArgumentParser(hf,k)
            data = np.std(data, axis=1)

        elif aggreg == 'min':
            data = ArgumentParser(hf,k)
            data = np.amin(data,axis=1)

        elif aggreg == 'max':
            data = ArgumentParser(hf,k)
            data = np.amax(data,axis=1)

        elif aggreg == 'mode':
            data = ArgumentParser(hf,k)
            data = stats.mode(data)
            data = data[0]


        elif aggreg == 'geomean':
            data = ArgumentParser(hf,k)
            data = stats.gmean(data, axis=1)


        elif aggreg == 'rms':
            data = ArgumentParser(hf,k)
            #Calculate root mean squared here?

        elif aggreg == 'initial' or aggreg == 'final':
            data = [d.decode() for d in hf[k]]
            data = [float(i) for i in data]

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

    return hf[k].attrs.get('Units')

def ArgumentParser(hf,k):
    forward = k.rpartition('_')[0] + '_forward'
    data = HFD5Decoder(hf,forward)
    return(data)

def HFD5Decoder(hf,k):
    data = [float(v.decode()) for d in hf[k] for v in d]
    shape = hf[k].shape
    data = np.reshape(data,(shape))
    return data

def ExtractUniqueValues(hf,k):
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

    if len(hf[k].shape) != 1:
        data = HFD5Decoder(hf,k)
        data.flatten()
    else:
        data = [d.decode() for d in hf[k]]
        del data[0]
        data = [float(i) for i in data]

    unique = np.unique(data)
    return unique

def CreateMatrix(xaxis,yaxis,zarray, orientation=1):
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
        print("ERROR: Cannot reshape",zarray,"into shape("+xnum+","+ynum+")")

    zmatrix = np.reshape(zarray, (ynum, xnum))
    zmatrix = np.flipud(zmatrix)

    for i in range(0,orientation):
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

def PrintDictData(data):
    """Proceses through dictionary and prints keys and first 6 values."""

    for k, v in data.items():

        print(k, ':', v[:])
        print()

def WriteOutput(inputfile, columns,file="bigplanet.out",delim=" ",header=False,ulysses=False):
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

    export = np.array(export)

    if ulysses == True:
        delim = ','
        header = True
        file = 'User.csv'

    if delim == "":
        print('ERROR: Delimiter cannot be empty')
        exit()

    with open(file, "w", newline="") as f:
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

def CreateHDF5File(InputFile):
    max_cores = mp.cpu_count()
    parallel_run_planet(InputFile,max_cores)
