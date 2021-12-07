Options
=======

Here is a table of each of the options that can be set in the ``BigPlanet`` input file. 

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
|                   | a BigPlanet file (.bpf) or a csv   | OR                                   |                        |
|                   | (.csv)                             |                                      |                        |
|                   |                                    | sOutputFile Test.csv                 |                        |
+-------------------+------------------------------------+--------------------------------------+------------------------+
| bUlysses          | Output the data into VR Ulysses    | bUlysses True                        |                        |
|                   | format. If set to true, then       |                                      |                        |
|                   | sOutputFile is automatically set   |                                      |                        |
|                   | to `User.csv`.                     |                                      |                        |
+-------------------+------------------------------------+--------------------------------------+------------------------+
| sSimName          | The name of a specific simulation  | sSimName test001/                    |                        |
|                   | to extract from an archive file.   |                                      |                        |
+-------------------+------------------------------------+--------------------------------------+------------------------+
| saBodyFiles       | A list of the body file names in   | saBodyFiles earth.in sun.in          | Yes                    |
|                   | each of the simulations            |                                      |                        |
+-------------------+------------------------------------+--------------------------------------+------------------------+
| sPrimaryFile      | The name of the primary file       | sPrimaryFile vpl.in                  | Yes                    |
|                   | (usually is called vpl.in)         |                                      |                        |
+-------------------+------------------------------------+--------------------------------------+------------------------+
| saKeyInclude      | The list of keys to export to the  | saKeyInclude earth:obliquity:forward |                        |
|                   | BigPlanet file. Multiple line      |                                      |                        |
|                   | arguments can be input with a      |                                      |                        |
|                   | trailing `$`.                      |                                      |                        |
+-------------------+------------------------------------+--------------------------------------+------------------------+
| saKeyExclude      | The list of key the user wants to  | saKeyExclude sun:luminosity:final    |                        |
|                   | *exclude* from the filtered file.  |                                      |                        |
|                   | This is mutually exclusive to      |                                      |                        |
|                   | saKeyInclude.                      |                                      |                        |
+-------------------+------------------------------------+--------------------------------------+------------------------+

