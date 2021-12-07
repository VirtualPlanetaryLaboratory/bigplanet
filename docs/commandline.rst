Command Line Usage
==================

Using ``BigPlanet`` on the command line is relatively straight forward. After a suite of
simulations (set up with `VSPACE <https://github.com/VirtualPlanetaryLaboratory/vspace>`_)
has completed, simply run the following command in the in the command line:

.. code-block:: bash

    BigPlanet <input file> -c [number of cores] -m [email] -aoqv

where the input file is the bpl.in file, which is explained `here <filetypes>`_.

There are three optional arguments:

:code:`-a` : create a BigPlanet archive

:code:`-c` : set the number of processors to use

:code:`-m` : emails the user when ``BigPlanet`` is complete

:code:`-o` : overwrite an existing archive

:code:`-q` : quiet mode (nothing is printed to the terminal)

:code:`-v` : verbose mode (all output is printed to the terminal)
