#!/usr/bin/env python

import os
import subprocess as sub
import sys
from itertools import chain


def DollarSign(m_bl, m_line, m_num, m_file):
    '''Process each line looking for $ at the end, continue until no $ present'''
    if m_line[-1] == '$':
        m_bl.append(m_line[0:-1])
        DollarSign(m_bl, m_file[m_num + 1], (m_num + 1), m_file)
    else:
        m_bl.append(m_line[0:])


def ReadFile(bplSplitFile, verbose=False, archive=False):

    includelist = []
    excludelist = []
    bodylist = []
    bpl_file = ""
    Ulysses = 0
    folder_name = ""
    SimName = ""

    with open(bplSplitFile, 'r') as input:
        # first thing we check is if both include and exclude are in the file bc that is bad
        if 'saKeyInclude' and 'saKeyExclude' in input.read():
            print("ERROR: saKeyInclude and saKeyExclude are mutually exclusive")
            exit()

    with open(bplSplitFile, 'r') as input:
        # now we loop over the file and get the various inputs
        content = [line.strip().split() for line in input.readlines()]
        for num, line in enumerate(content):
            if line:
                # we get the folder where the raw data is stored and have the default output file name set
                if line[0] == 'sDestFolder':
                    folder_name = line[1]
                    outputFile = folder_name.split('/')[-1] + "_filtered.bpf"
                if line[0] == 'sArchiveFile':
                    bpl_file = line[1]
                if line[0] == 'sOutputFile':
                    outputFile = line[1]
                if line[0] == 'sPrimaryFile':
                    primaryFile = line[1]
                if line[0] == 'bUlysses':
                    Ulysses = 1
                if line[0] == 'sSimName':
                    SimName = line[1]

                if line[0] == "saBodyFiles":
                    DollarSign(bodylist, line[1:], num, content)
                    bodylist = list(chain.from_iterable(bodylist))

                if line[0] == 'saKeyInclude':
                    DollarSign(includelist, line[1:], num, content)
                    includelist = list(chain.from_iterable(includelist))

                if line[0] == 'saKeyExclude':
                    DollarSign(excludelist, line[1:], num, content)
                    excludelist = list(chain.from_iterable(excludelist))

        if not bpl_file and not includelist and archive == False or not bpl_file and not excludelist and archive == False:
            print("Error: No BPL Archive file or Include/Exclude List detected.")
            exit()
            #print("WARNING: This may take some time...")

        if not folder_name:
            print("ERROR: No sDestFolder found in bpl.in file")
            exit()

        if Ulysses == 1:
            outputFile = 'User.csv'
            print("WARNING: Ulysses is set to True. Changed Output file to User.csv")

            # if the simName is some value we need to check if all the keys are forward
            if SimName:
                for i in includelist:
                    if 'forward' not in i:
                        print(
                            "ERROR: SimName must only use forward file data for output")
                        exit()
                for j in excludelist:
                    if 'forward' not in j:
                        print(
                            "ERROR: SimName must only use forward file data for output")
                        exit()

        if Ulysses == True and SimName == "":
            for i in includelist:
                if 'forward' in i:
                    print(
                        "ERROR: Forward keys in saKeyInclude requires sSimName for Ulysses Output")
                    exit()
            for j in excludelist:
                if 'forward' in j:
                    print(
                        "ERROR: Forward keys in saKeyExclude requires sSimName for Ulysses Output")
                    exit()

        if verbose:
            print("Folder Name:", folder_name)

            print("BPL Archive File:", bpl_file)
            print("Include List:", includelist)
            print("Exclude List:", excludelist)
            print("Output File:", outputFile)
            print("Ulysses Output:", Ulysses)
            print("Simulation Name:", SimName)
            print("Body Files:", bodylist)
            print("Primary File:", primaryFile)

        return folder_name, bpl_file, outputFile, bodylist, primaryFile, includelist, excludelist, Ulysses, SimName


def GetDir(vspace_file):
    """ Give it input file and returns name of folder where simulations are located. """

    infiles = []
    # gets the folder name with all the sims
    with open(vspace_file, 'r') as vpl:
        content = [line.strip().split() for line in vpl.readlines()]
        for line in content:
            if line:
                if line[0] == 'sDestFolder':
                    folder_name = line[1]

                if line[0] == 'sBodyFile' or line[0] == 'sPrimaryFile':
                    infiles.append(line[1])
    if folder_name is None:
        raise IOError("Name of destination folder not provided in file '%s'."
                      "Use syntax 'destfolder <foldername>'" % vspace_file)

    if os.path.isdir(folder_name) == False:
        print("ERROR: Folder", folder_name,
              "does not exist in the current directory.")
        exit()

    return folder_name, infiles


def GetSims(folder_name, simname=""):
    """ Pass it folder name where simulations are and returns list of simulation folders. """
    # gets the list of sims
    sims = sorted([f.path for f in os.scandir(
        os.path.abspath(folder_name)) if f.is_dir()])

    if simname:
        sims = [x for x in sims if simname in x]

    print(sims)
    return sims


def GetSNames(bodyfiles, sims):
    # get system and the body names
    body_names = []

    for file in bodyfiles:
        # gets path to infile
        full_path = os.path.join(sims[0], file)
        # if the infile is the primary file, then get the system name
        if bodyfiles[-1] == file:
            with open(full_path, 'r') as vpl:
                content = [line.strip().split() for line in vpl.readlines()]
                for line in content:
                    if line:
                        if line[0] == 'sSystemName':
                            system_name = line[1]
        # otherwise get the sName from the body files
        else:
            with open(full_path, 'r') as infile:
                content = [line.strip().split() for line in infile.readlines()]
                for line in content:
                    if line:
                        if line[0] == 'sName':
                            body_names.append(line[1])

    return system_name, body_names


def GetVplanetHelp():
    command = "vplanet -H | egrep -v '^$|^\+' | cut -f 2,4 -d '|' | egrep '^ \*\*|^ Cust|^ Type|^ Dim|^ Defa|^Output Parameters'"
    py_ver = sys.version.split()[0]
    if '3.6' in py_ver:
        proc = sub.run(command, shell=True, universal_newlines=True,
                       stdout=sub.PIPE, stderr=sub.PIPE)
    else:
        proc = sub.run(command, shell=True, text=True,
                       stdout=sub.PIPE, stderr=sub.PIPE)
    output = proc.stdout.splitlines()

    vplanet_dict = {}

    for count, line in enumerate(output):
        if ((line.startswith(' **b') or line.startswith(' **d') or line.startswith(' **i') or line.startswith(' **s')) or line.startswith(' **sa') and len(line.split()) == 1):

            option = line.strip("** ")
            # print("Option:",option)
            vplanet_dict[option] = {}
            num = count + 1
            while num != count:
                if "Type" in output[num]:
                    tp = output[num].rpartition('|')[-1].strip()
                    vplanet_dict[option]['Type'] = tp
                    # print("Type:",tp)
                    num += 1

                elif "Custom unit" in output[num]:
                    custom_unit = output[num].rpartition('|')[-1].strip()
                    vplanet_dict[option]['Custom Unit'] = custom_unit
                    #print("Custom Unit:",custom_unit)
                    num += 1

                elif "Dimension(s)" in output[num]:
                    dim = output[num].rpartition('|')[-1].strip()
                    vplanet_dict[option]['Dimension'] = dim
                    # print("Dimension:",dim)
                    num += 1

                elif "Default value" in output[num]:
                    default = output[num].rpartition('|')[-1].strip()
                    vplanet_dict[option]['Default Value'] = default
                    #print("Default Value",default)
                    # print()

                    num += 1

                elif "**" in output[num]:
                    num = count

                else:
                    num += 1

        if "Output Parameters" in line:
            break

    return vplanet_dict


def GetLogName(in_files, sims, system_name):
    prefix = system_name

    for file in in_files:
        full_path = os.path.join(sims[0], file)
        with open(full_path, 'r') as vpl:
            content = [line.strip().split() for line in vpl.readlines()]
            for line in content:
                if line:
                    if line[0] == 'sLogfile':
                        prefix = line[1]
    logfile = prefix + ".log"

    return logfile


# def GetForwardBackwards(in_files,sims,system_name):

#     prefix = system_name
#     #check if sOutfile in body files
#     #check if bDoFoward or bDoBackward in primaryfile
#     #if sOutfile in body files and bDoForward true,
#     #then return the name and forward = true
#     #if outfile is not in body files, and bDoforward is true,
#     #then return the default name
