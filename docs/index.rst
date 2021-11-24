Bigplanet Documentation
=======================

Bigplanet is software to compress a large number of `VPLanet <https://github.com/VirtualPlanetaryLaboratory/vplanet>`_ 
for long term storage and rapid data analysis. It has been designed to work in conjunction
with the `vspace <https://github.com/VirtualPlanetaryLaboratory/vspace>`_ and `multi-planet 
<https://github.com/VirtualPlanetaryLaboratory/multi-planet>`_ scripts that generate a 
set of initial conditions files and perform the simulations across multi-core platforms, 
respectively. 

Bigplanet has three primary use cases: 1) To compress an entire suite of ``VPLanet``
runs into a single "bigplanet archive" file, 2) to extract a subset of data into a 
"bigplanet file" for rapid analyses, and 3) for use in a python script for plotting with 
matplotlib. 

Bigplanet compresses your parameter sweep into a specifically formatted HDF5 file that
can be 50% the size of the raw data. This file is called a bigplanet archive and typically
has the extensions ``.bpa``. As bigplanet compresses *all* the data, you can safely delete
the raw data once the archive file is created. Note that bigplanet will also create an 
md5checksum file that monitors the integrity of the archive. Accessing data from the archive
can be 2-10 times faster than from the raw ASCII text data, depending on the raw data.

While it is possible to perform analyses and plot outputs from the archive file, it is
often still painfully slow for parameter sweeps consisting of 10,000 simulations or more.
Thus, bigplanet can also create bigplanet files, typically with extension .bpf, that contain
much smaller subsets of the data. Bigplanet files can also contain statistics of a simulation,
such as the minimum eccentricity.

For a suite of ~10,000 simulations, it can take 30 minutes or more to build an archive
files and 10s of seconds to build a bigplanet file. The advantage of using bigplanet is
that when it comes time to plot outputs, reading from a bigplanet file takes less than 1
second (usually) and so you can quickly develop your plotting script and generate a 
publication-worthy figure in a fraction of the time as a standard approach that much 
enter each subdirectory and open each file to extract a single parameter from each simulation.

The following links provide more in-depth explanations on how to get the most out of bigplanet.

.. toctree::
   :maxdepth: 1

   install
   quickstart
   inputfile
   filetypes
   Keys
   commandline
   Script
   examples
   GitHub <https://github.com/VirtualPlanetaryLaboratory/bigplanet>
