Quickstart Guide
================


Tutorial that walks the user through how to use bigplanet with an example case (small) creating a filtered file

assume user has ran vspace + multiplanet, use bigplanet to access the data fast
this explains how to turn raw data -> BPA file
create filtered file for fast analysis

.. code-block:: bash
    
    bigplanet bpl.in -a 

This will create the archive file, but lets first look at the bpl.in file.

.. code-block:: bash

    sDestFolder GDwarf_exp10000
    sArchiveFile GDwarf_exp10000.bpa
    sOutputFile Test.bpf

    saBodyFiles earth.in sun.in
    sPrimaryFile vpl.in

    saKeyInclude earth:Obliquity:forward earth:Instellation:final earth:IceBeltLand:final $
    earth:IceBeltSea:final earth:IceCapNorthLand:final earth:IceCapNorthSea:final $
    earth:IceCapSouthLand:final earth:IceCapSouthSea:final earth:IceFree:final earth:Snowball:final

On line 1 is the folder where the raw data are located

On line 2 is the name of archive file

On line 3 is the Output file which is ignored with the -a option. The output file is the name of the filtered file which will be created later

On line 5 is a list of body files

On line 6 is the primary file (in this case its vpl.in)

On lines 8-10 is the key names that are included in the output file. Similarly to line 3, these lines are ignored when the -a option is passed

To extract the data from the Archive, run the following command:

.. code-block:: bash
    
    bigplanet bpl.in

This now *does* use lines 3 and 7-9 to create the filtered file, which only contains the data the user is interested in.
From here checkout Scripting with bigplanet page for the next steps in analysing your data.