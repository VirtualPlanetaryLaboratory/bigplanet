Running bigplanet
=================

This tutorial describes how to quickly get started with bigplanet and assumes you
are already familiar with VPLanet. Furthermore, it assumes you have already performed
a set of simulations with vspace and multiplanet. In this case, we will build both a 
bigplanet archive and a bigplanet file.

To execute ``bigplanet`` from the command line and build an archive, use the command:

.. code-block:: bash
    
    bigplanet bpl.in -a 

This will read in the instructions in the ``bpl.in`` file and the ``-a`` flag tells
``bigplanet`` to create an archive file. To see how, let's look inside bpl.in.

.. code-block:: bash
    :linenos:

    sDestFolder GDwarf_exp10000
    sArchiveFile GDwarf_exp10000.bpa
    sOutputFile ice_states.bpf

    saBodyFiles earth.in sun.in
    sPrimaryFile vpl.in

    saKeyInclude earth:Obliquity:forward earth:Instellation:final earth:IceBeltLand:final $
    earth:IceBeltSea:final earth:IceCapNorthLand:final earth:IceCapNorthSea:final $
    earth:IceCapSouthLand:final earth:IceCapSouthSea:final earth:IceFree:final earth:Snowball:final

Line 1 is the folder where the raw data are located and line 2 is the name of archive file 
to be generated. The remaining lines are all ignored when the -a flag is set. 

After the archive is built, it is often convenient to extract a small amount of data from the archive 
file (GDwarf_exp10000.bpa) for detailed analysis. To create the bigplanet file, run the 
same command as above, but *without* the -a flag:

.. code-block:: bash
    
    bigplanet bpl.in

Let's now look at how ``bigplanet`` interprets the bpl.in file without the -a flag.

Since Line 2 provides the name of a bigplanet archive, ``bigplanet`` will not look to
extract the appropriate columns from the raw data, but from the archive.

Line 3 is the name of the bigplanet file.

Line 5 is the list of body files from which to extract the columns *XXX should sun.in be here?? XXX*

Line 6 is the name of primary file (in this case its vpl.in).


Lines 8-10 list the `key <Keys>`_ names that are included in the output file. 

The resulting bigplanet file (ice_states.bpf) contains a set of columns, in HDF5 format,
that correspond to the listed keys.

You can then use ``bigplanet``'s `scripting <Script>`_ capability to easily convert these 
columns into plots or perform other types of analyses.