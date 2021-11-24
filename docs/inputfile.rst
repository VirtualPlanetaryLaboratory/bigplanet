The Bigplanet Input File
========================

Overview
--------

The Bigplanet input file tells bigplanet the various information about your parameter 
sweep. An example bigplanet input file, called :code:`bpl.in` is described below:

.. code-block:: bash
    
    sDestFolder GDwarf_exp10000
    sBigplanetFile GDwarf_exp10000.bpa
    sOutputFile Test.bpf

    saBodyFiles earth.in $
                sun.in
                
    sPrimaryFile vpl.in

    saKeyInclude earth:Obliquity:forward earth:Instellation:final earth:IceBeltLand:final $
    earth:IceBeltSea:final earth:IceCapNorthLand:final earth:IceCapNorthSea:final $
    earth:IceCapSouthLand:final earth:IceCapSouthSea:final earth:IceFree:final earth:Snowball:final

Where users can use a variety of variables for their bigplanet run. Below is a table of each of the variables
that can be seen in the input file. 

Options
-------

+-------------------+------------------------------------+--------------------------------------+------------------------+
| **Variable**      | **Description**                    | **Example**                          | **Required Arguments** |
+-------------------+------------------------------------+--------------------------------------+------------------------+
| sDestFolder       | The folder where the raw           | sDestFolder GDwarf                   | Yes                    |
|                   | data is stored                     |                                      |                        |
+-------------------+------------------------------------+--------------------------------------+------------------------+
| sArchiveFile      | The name of the Bigplanet          | sArchiveFile GDwarf.bpa              |                        |
|                   | Archive file (.bpa)                |                                      |                        |
+-------------------+------------------------------------+--------------------------------------+------------------------+
| sOutputFile       | The name of the Output file.       | sOutputFile Test.bpf                 |                        |
|                   | Note that this can be either       |                                      |                        |
|                   | a bplanet filtered file (.bpf)     | OR                                   |                        |
|                   | or a csv (.csv)                    |                                      |                        |
|                   |                                    | sOutputFile Test.csv                 |                        |
+-------------------+------------------------------------+--------------------------------------+------------------------+
| bUlysses          | Flag if the user wants a           | bUlysses True                        |                        |
|                   | VR Ulysses output. If set to true, |                                      |                        |
|                   | then sOutputFile is automatically  |                                      |                        |
|                   | set to `User.csv`.                 |                                      |                        |
+-------------------+------------------------------------+--------------------------------------+------------------------+
| sSimName          | If a user wants to output data     | sSimName test001/                    |                        |
|                   | from either a forward, backward or |                                      |                        |
|                   | climate file for VR Ulysses, this  |                                      |                        |
|                   | must be set to the particular      |                                      |                        |
|                   | simulation the user wants to view  |                                      |                        |
+-------------------+------------------------------------+--------------------------------------+------------------------+
| saBodyFiles       | A list of the body file names in   | saBodyFiles earth.in sun.in          | Yes                    |
|                   | each of the simulations            |                                      |                        |
+-------------------+------------------------------------+--------------------------------------+------------------------+
| sPrimaryFile      | the name of the primary file       | sPrimaryFile vpl.in                  | Yes                    |
|                   | (usually is called vpl.in in       |                                      |                        |
|                   | most cases)                        |                                      |                        |
+-------------------+------------------------------------+--------------------------------------+------------------------+
| saKeyInclude      | the list of keys the user wants    | saKeyInclude earth:obliquity:forward |                        |
|                   | to export in the output file.      |                                      |                        |
|                   | If the line is too long end it     |                                      |                        |
|                   | with a `$` and continue on the     |                                      |                        |
|                   | next line                          |                                      |                        |
+-------------------+------------------------------------+--------------------------------------+------------------------+
| saKeyExclude      | the list of key the user wants to  | saKeyExclude sun:luminosity:final    |                        |
|                   | *exclude* from the filtered file.  |                                      |                        |
|                   | This is mutually exclusive to      |                                      |                        |
|                   | saKeyInclude.                      |                                      |                        |
+-------------------+------------------------------------+--------------------------------------+------------------------+


VR Ulysses Output
-----------------

WIth bigplanet, the user can output as a VR Ulysses file. To do so, the :code:`bpl.in` file could look
like this:  

.. code-block:: bash
    
    sDestFolder GDwarf_exp10000
    sBigplanetFile GDwarf_exp10000.bpa

    bUlysses True
    sSimName test_001

    saBodyFiles earth.in sun.in
    sPrimaryFile vpl.in

    saKeyInclude earth:Obliquity:forward

.. note::

    sSimName is only used when saKeyInclude has forward file keys *ie* earth:oblquity:final 
    If extracting logfile information, that variable is not needed. 

