Understanding Keys
==================

Keys are the bread and butter of ``BigPlanet``. The keys are the names of the  
variables that can be extracted from a BigPlanet archive.


.. note::

	  Keys using the following format for naming: body:parameter:aggregation, where "aggregation" is an aspect of the variable.


Below is a table of aggregations related to input and output files:


+-------------------+--------------------------------------------------------------------------+
| Aggregation       | Description                                                              |
+-------------------+--------------------------------------------------------------------------+
| Initial           | The initial values of a parameter as listed in the log file              |
+-------------------+--------------------------------------------------------------------------+
| Final             | The final values of a parameter as listed in the log file                |
+-------------------+--------------------------------------------------------------------------+
| Option            | The parameter's argument to an option in the input file                  |
+-------------------+--------------------------------------------------------------------------+
| Forward           | A list of the parameter's values in the forward file.                    |
+-------------------+--------------------------------------------------------------------------+
| Backward          | A list of the parameter's values in the backward file.                   |
+-------------------+--------------------------------------------------------------------------+
| Climate           | A list of the parameter's climate values (*POISE only*).                 |
+-------------------+--------------------------------------------------------------------------+
| OutputOrder       | A list of the parameters and units assoicated with saOutputOrder.        |
+-------------------+--------------------------------------------------------------------------+
| GridOutput Order  | A list of the names and units of the climate file (*POISE only*).        |
+-------------------+--------------------------------------------------------------------------+

In addition, variables that are listed in ``VPLanet`` forward or backward files also have a set of statistical 
aggretations that can be applied. Use one of these to quickly obtain metadata on a particular variable. For 
example, Earth:Eccentricity:Min would return the minimum values of eccentricity recorded for every simulation.

+--------------------+-----------------------------------------------------------------------+
| Aggregation        | Description                                                           |
+--------------------+-----------------------------------------------------------------------+
| Min                | The minimum values of a parameter recorded for each simulation.       |
+--------------------+-----------------------------------------------------------------------+
| Max                | The maximum values of a parameter recorded for each simulation.       |
+--------------------+-----------------------------------------------------------------------+
| Mean               | The arithmetic means of a parameter recorded for each simulation.     |
+--------------------+-----------------------------------------------------------------------+
| Geometric Mean     | The geometric means of a parameter recorded for each simulation.      |
+--------------------+-----------------------------------------------------------------------+
| Standard Deviation | The standard deviations of a parameter recorded for each simulation.  |
+--------------------+-----------------------------------------------------------------------+

.. warning::

    The preceding aggregations will **only** work with parameters that are
    from the *forward* or *backward* file.