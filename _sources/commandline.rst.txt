Command Line
==================
Using BigPlanet on the command line is relatively straight forward. After a suite of
simulations (set up with `vspace <../vspace>`_) has completed, simply run the following
command in the in the command line:

.. code-block:: bash

    bigplanet <input file> -c [number of cores] -q -m [email]

where the input file is the bpl.in file, which is explained here.

There are three optional arguments:

:code:`-c` : the number of processors used

:code:`-q` : quiet mode (nothing is printed to the command line)

:code:`-v` : verbose mode (more output is printed to the command like)

:code:`-m` : emails the user when Bigplanet is complete

:code:`-o` : overrides the creation of a bigplanet archive file if it already exists

:code:`-a` : flag for bigplanet filtered file

