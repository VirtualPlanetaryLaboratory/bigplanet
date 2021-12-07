BigPlanet Documentation
=======================

``BigPlanet`` is software to compress a large number of `VPLanet <https://github.com/VirtualPlanetaryLaboratory/vplanet>`_ 
simulations for long-term storage *and* rapid data analysis. It has been designed to work in conjunction
with the `VSPACE <https://github.com/VirtualPlanetaryLaboratory/vspace>`_ and `multi-planet 
<https://github.com/VirtualPlanetaryLaboratory/multiplanet>`_ scripts that generate a 
set of initial conditions files and perform the simulations across multiple cores, 
respectively. 

``BigPlanet`` has three primary use cases: 1) To compress an entire suite of ``VPLanet``
runs into a single "BigPlanet archive" for long-term storage, 2) to extract a subset of data into a 
"BigPlanet file" for rapid analyses, and 3) for use in a python script for plotting with 
matplotlib. 

``BigPlanet`` compresses your parameter sweep into a formatted HDF5 file that
can be 50% smaller than the raw data. This file is called a BigPlanet archive and typically
has the extension ``.bpa``. As a BigPlanet archive contains *all* the data from your parameter 
sweep, you can safely delete
the raw data once the archive is created. Note that ``BigPlanet`` will also create an 
MD5 checksum file that monitors the integrity of the archive. Accessing data from the archive
is at least 10 times faster than from the raw ASCII text data.

While it is possible to perform analyses and plot outputs from the archive, it is
often still painfully slow for parameter sweeps consisting of 10,000 simulations or more.
Thus, ``BigPlanet`` can also create BigPlanet files, typically with extension ``.bpf``, that contain
much smaller subsets of the data. BigPlanet files can also contain statistics of a simulation,
such as the minimum eccentricity.

For a suite of ~10,000 simulations, it can take 30 minutes or more to build an archive
file and 10s of seconds to build a BigPlanet file. The advantage of ``BigPlanet`` is
that when it comes time to plot results, reading from a BigPlanet file takes less than 1
second (usually). This speed enables users to quickly develop plotting script to generate 
publication-worthy figures in a fraction of the time required for the standard approach 
(opening each relevant file to extract a single parameter from each simulation).

The following links provide more in-depth explanations on how to get the most out of BigPlanet.

.. toctree::
   :maxdepth: 1

   install
   quickstart
   options
   filetypes
   Keys
   commandline
   Script
   examples
   GitHub <https://github.com/VirtualPlanetaryLaboratory/BigPlanet>

.. note::

    To maximize BigPlanet's power, run ``VSPACE`` and ``MultiPlanet -bp`` to automatically
    build the BigPlanet archive immediately after the simulations finish.  Then create 
    BigPlanet files from the archive as needed, and use ``BigPlanet``'s scripting functions to 
    extract vectors and matrices for plotting, statistical analyses, etc.