Meshhandler
===========

This module contains currently only a simulation, for how knitpieces
adapt to surfaces. 

Simulation abstract
-------------------

The surface has a rectangular shape, with 4 distinct borderlines;
up, left, down and right. These borderlines correspond to the knitpiece 
borders. Those borders can be obtained via 
:py:meth:`createcloth.strickgraph.strickgraph.get_borders`.


clothfactory parts
------------------

The function :py:func:`createcloth.meshhandler.relax_gridgraph` is 
implemented via 
:py:data:`relax_strickgraph_on_surface<clothfactory_parts.physics.relax_strickgraph_on_surface.relax_strickgraph_on_surface>`.
That factoryleaf produces from a corresponding map, saved via 
:py:class:`map_for_strickgraph<clothfactory_parts.physics.relax_strickgraph_on_surface.map_for_strickgraph>`
and a knitpiece, saved via 
:py:class:`strickgraph_container<clothfactory_parts.strickgraph.strickgraph_datatypes.strickgraph_container>`
spatialdata about the knit piece and saves it under
:py:class:`strickgraph_spatialdata<clothfactory_parts.strickgraph.strickgraph_datatypes.strickgraph_spatialdata>`.

References
----------

.. autofunction:: createcloth.meshhandler.relax_gridgraph
