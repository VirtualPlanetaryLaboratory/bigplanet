Understanding Keys
==================
Keys are the bread and butter of BigPlanet. The keys are the names of the various 
variables that BigPlanet has extracted from the forward file, the option files, 
and the log file that are generated when VPLanet finishes compiling.


.. note::

	  Keys using the following format for naming: body:variable:aggregation


Below is a table of all the various aggregations available at this time:

.. list-table::
   :widths: auto
   :header-rows: 1

   * - Aggregation
     - Description
     - Usage
   * - Initial
     - returns a list of the *initial* values of the particular parameter for
       every simulation. This data is from the log file.
     - body:variable:initial
   * - Final
     - returns a list of the *final* values of the particular parameter for
       every simulation. This data is from the log file.
     - body:variable:final
   * - Output Order
     - returns a list of the names and units of the forward file values. 
       This data is from the log file.
     - body:OutputOrder
   * - Forward
     - returns a nested list of the *forward* values of the particular
       parameter for every simulation. This data is from the forward file.
     - body:variable:forward
   * - Grid Output Order
     - if the Poise Module was used in the simulations,returns a list of the
       names and units of the climate file values. This data is from the log file.
     - body:GridOutputOrder
   * - Climate
     - if the Poise Module was used in the simulations, the climate options
       returns a nested list of the *climate* values of the particular
       parameter for every simulation. This data is from the climate files.
     - body:variable:climate
   * - Option
     - the option options returns a  list of the *option* values of the particular
       parameter for every simulation. This data is from the option files.
     - body:variable:option


.. warning::

    The following aggregations will **only** work with parameters that are
    from the *forward* file.
    If you attempt to use it with a value that is **NOT** in the forward file,
    it will produce an error.
 
Below is a table of all the various stastical available at this time:

 .. list-table::
    :widths: auto
    :header-rows: 1

    * - Aggregation
      - Description
      - Usage
    * - Min
      - returns a list of the minimum values from the *forward* values of the
        particular parameter for every simulation
      - body:variable:min
    * - Max
      - returns a list of the maximum values from the *forward* values of the
        particular parameter for every simulation
      - body:variable:max
    * - Mean
      - returns a list of the mean calculated from the *forward* values of the
        particular parameter for every simulation
      - body:variable:mean
    * - Geometric Mean
      - returns a list of the gemoetric mean calculated from the *forward*
        values of the particular parameter for every simulation
      - body:variable:geomean
    * - Standard Deviation
      - returns a list of the standard deviation calculated from the *forward*
        values of the particular parameter for every simulation
      - body:variable:stddev