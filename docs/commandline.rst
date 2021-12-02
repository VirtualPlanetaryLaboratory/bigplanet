Command Line Usage
==================

Using ``bigplanet`` on the command line is relatively straight forward. After a suite of
simulations (set up with `vspace <https://github.com/VirtualPlanetaryLaboratory/vspace>`_) 
has completed, simply run the following command in the in the command line:

.. code-block:: bash

    bigplanet <input file> -c [number of cores] -m [email] -aoqv

where the input file is the bpl.in file, which is explained `here <filetypes>`_.

There are three optional arguments:

:code:`-a` : create a bigplanet archive

:code:`-c` : set the number of processors to use

:code:`-m` : emails the user when ``bigplanet`` is complete

:code:`-o` : overwrite an existing archive

:code:`-q` : quiet mode (nothing is printed to the terminal)

:code:`-v` : verbose mode (all output is printed to the terminal)
