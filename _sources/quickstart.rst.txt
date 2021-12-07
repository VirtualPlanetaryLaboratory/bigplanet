Running BigPlanet
=================

This tutorial describes how to quickly get started with ``BigPlanet`` and assumes you
are already familiar with ``VPLanet``. Furthermore, it assumes you have already performed
a set of simulations with ``vspace`` and ``multiplanet``. In this case, we will build both a 
BigPlanet archive and a BigPlanet file.

To execute ``BigPlanet`` from the command line and build an archive, use the command:

.. code-block:: bash
    
    BigPlanet bpl.in -a 

This will read in the instructions in the ``bpl.in`` file and the ``-a`` flag tells
``BigPlanet`` to create an archive. To see how, let's look inside bpl.in.

.. code-block:: bash
    :linenos:

    sDestFolder GDwarf
    sArchiveFile GDwarf.bpa
    sOutputFile ice_states.bpf

    saBodyFiles earth.in sun.in
    sPrimaryFile vpl.in

    saKeyInclude earth:Obliquity:forward earth:Instellation:final earth:IceBeltLand:final $
        earth:IceBeltSea:final earth:IceCapNorthLand:final earth:IceCapNorthSea:final $
        earth:IceCapSouthLand:final earth:IceCapSouthSea:final earth:IceFree:final $
        earth:Snowball:final

Line 1 is the folder where the raw data are located and line 2 is the name of archive  
to be generated. The remaining lines are all ignored when the ``-a`` flag is set. We'll discuss those lines 
below.

After the archive is built, it is often convenient to extract a small amount of data from the archive 
(GDwarf.bpa) for detailed analysis. To create the BigPlanet file, run the 
same command as above, but *without* the ``-a`` flag:

.. code-block:: bash
    
    BigPlanet bpl.in

Let's now look at how ``BigPlanet`` interprets the bpl.in file without the ``-a`` flag.

Since Line 2 provides the name of a BigPlanet archive, ``BigPlanet`` will not look to
extract the appropriate columns from the raw data, but from the archive.

Line 3 is the name of the BigPlanet file that will contain the data subset.

Line 5 is the list of body files from which to extract the columns *XXX should sun.in be here?? XXX*

Line 6 is the name of primary file (in this case its vpl.in).


Lines 8-11 list the `key names <Keys>`_ that are included in the output file. Note that your list of keys
can span multiple lines by ending the line with a ``$`` symbol, just as with ``VPLanet``.

The resulting BigPlanet file (ice_states.bpf) contains a set of columns, in HDF5 format,
that correspond to the listed keys.

You can then use ``BigPlanet``'s `scripting <Script>`_ capability to easily convert these 
columns into plots or perform other types of analyses.

.. note::

    To maximize BigPlanet's power, run ``vspace`` and ``mulit-planet -bp`` to automatically
    build the BigPlanet archive immediately after the simualtions finish.  Then create 
    BigPlanet files from the archive as needed, and use ``BigPlanet``'s scripting functions to 
    extract vectors and matrices for plotting, statistical analyses, etc.