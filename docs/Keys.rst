Understanding Keys
==================
Keys are the bread and butter of BigPlanet. The keys are the names of the various 
variables that BigPlanet has extracted from the various files that are generated 
when VPLanet finishes compiling.


.. note::

	  Keys using the following format for naming: body:variable:aggregation


Below is a table of all the various aggregations available at this time:


+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------+
| Aggregation       | Description                                                                                                                                                                                      | Usage                  |
+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------+
| Initial           | returns a list of the *initial* values of the particular parameter for every simulation. This data is from the .log file                                                                         | body:variable:initial  |
+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------+
| Final             | returns a list of the *final* values of the particular parameter for every simulation. This data is from the .log file                                                                           | body:variable:final    |
+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------+
| Option            | returns a  list of the *option* values of the particular parameter for every simulation. This data is from the .in files                                                                         | body:variable:option   |
+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------+
| Forward           | returns a nested list of the *forward* values of the particular parameter for every simulation. This data is from the .forward file                                                              | body:variable:forward  |
+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------+
| Backward          | returns a nested list of the *backward* values of the particular parameter for every simulation. This data is from the .backward file                                                            | body:variable:backward |
+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------+
| Climate           | returns a nested list of the *climate* values of the particular parameter for every simulation. This data is from the .climate file (Only valid if the Poise Module was used in the simulations) | body:variable:climate  |
+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------+
| Output Order      | returns a list of the names and units of the forward file values.  This data is from the .log file.                                                                                              | body:OutputOrder       |
+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------+
| Grid Output Order | returns a list of the names and units of the climate file values.  This data is from the .log file. (Only valid if the Poise Module was used in the simulations)                                 | body:GridOutputOrder   |
+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------+


.. warning::

    The following aggregations will **only** work with parameters that are
    from the *forward* file.
    If you attempt to use it with a value that is **NOT** in the forward file,
    it will produce an error.
 
Below is a table of all the various stastical available at this time:

+--------------------+----------------------------------------------------------------------------------------------------------------------------------+-----------------------+
| Aggregation        | Description                                                                                                                      | Usage                 |
+--------------------+----------------------------------------------------------------------------------------------------------------------------------+-----------------------+
| Min                | returns a list of the *minimum* values from each of the forward files of the particular parameter for every simulation           | body:variable:min     |
+--------------------+----------------------------------------------------------------------------------------------------------------------------------+-----------------------+
| Max                | returns a list of the *maximum* values from each of the forward files of the particular parameter for every simulation           | body:variable:max     |
+--------------------+----------------------------------------------------------------------------------------------------------------------------------+-----------------------+
| Mean               | returns a list of the *mean* values from each of the forward files of the particular parameter for every simulation              | body:variable:mean    |
+--------------------+----------------------------------------------------------------------------------------------------------------------------------+-----------------------+
| Geometric Mean     | returns a list of the *geometric mean* values from each of the forward files of the particular parameter for every simulation    | body:variable:geomean |
+--------------------+----------------------------------------------------------------------------------------------------------------------------------+-----------------------+
| Standard Deviation | returns a list of the *standard devation* values from each of the forward files of the particular parameter for every simulation | body:variable:stddev  |
+--------------------+----------------------------------------------------------------------------------------------------------------------------------+-----------------------+
