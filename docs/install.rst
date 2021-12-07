Installation Guide
==================

There are two ways to install ``BigPlanet``: 1) in conjunction with 
`VPLanet <https://github.com/VirtualPlanetaryLaboratory/vplanet>`_ and 
its other support scripts, or 2) from source.

To install ``BigPlanet`` and the other ``VPLanet`` packages, use the command:

.. code-block:: bash

    python -m pip install vplanet

To install from source, first close the repo:


.. code-block:: bash

    git clone https://github.com/VirtualPlanetaryLaboratory/bigplanet.git

and then go into the directory (BigPlanet) and run the setup script:

.. code-block:: bash

    cd BigPlanet
    python setup.py install


The setup script installs the various dependencies and allows ``BigPlanet`` to be
run from the `command line <commandline>`_ as well as be imported as a 
`Python module <Script>`_.
