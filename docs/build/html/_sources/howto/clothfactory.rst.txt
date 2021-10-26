Howto to autothingy clothes
===========================

Clothfactory program derived from datagraph_factory to create knit pieces 
from 3d-objects. 

As a standalone it can be executed, by creating a startdirectory with the
builtin program :py:mod:`myprogram.asd` and with the autocomplete program
of datagraph_factory :py:mod:`datagraph_factory.complete_directory`

.. code::

   python -m clothfactory_parts.programs.create_directory_strickcompleter <directory>
   python -m datagraph_factory.complete_directory <directory>

After that we can read the information from the directory: :program:`create_directory_strickcompleter`

.. code::

   python -m myprogram.visualize_strick <directory>
   # This plots the knitpiece with the available spatial information

   python -m myprogram.create_knitmanuals <directory>
   # This prints the knitmanuals

Overview other available and targetted data
-------------------------------------------

As otherview i will sort to following corresponding categories:

        * Objectinfo - 3d information about the body - static
        * Yarn- and Knittingpattern - Information which knits are used and what \
          physical properties they have - static
        * Information about the knitting piece - variable

Objectinfo
~~~~~~~~~~

This information includes spatialdescription of the object, for that our knitting piece is made. A quick bulletpoint overview:

        * description via mesh, that means via vertices (3d) and faces.
        * subsurfaceinformation, that means which rectangles will be covered \
          with each one knitting piece

A detailled overview:

        1. 3d-vertices
        2. (edges consisting of 2 vertice-indices)
        3. faces consisting of n-vertice-indices
        4. subsurfaces consisting of n-face-indices
        5. subsurface-maps, which convert the 3d-space of the corresponding \
           submesh to a 2d-maplike representation

For reference i have listed all corresponding datagraphnodes: 1-5 is saved in
:py:class:`clothfactory.ply_surface`. There is also a connection to 
:py:class:`clothfactory.mesh_2dmap` but im not sure how this turns out.


Yarn- and knittinginformation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This information comprises:
        * knittingpattern information - meaning how the knitpiece is made, \
          when it should e.g. expand fromm line to line
        * Yarninformation - Information mainly for spatialsimulation of the \
          knittingpiece. E.g. how big a stitch is.

For further information see :py:mod:`createcloth.stitchinfo`, \
:py:mod:`createcloth.plainknit` and :py:mod:`createcloth.physicalhelper`.
The stitchinfo is stored within the datagraphnode \
:py:class:`strickgraph_stitchdata`.
The manner in which this information is stored is *work-in-progres*. So \
please, feel free to check in the reference, how the data is stored.


Knittingpiece
~~~~~~~~~~~~~

This is the part we want to be simulated. This information describes our \
Knittinpiec in detail:

        * knittingmanuals for each knittingpiece
        * also spatialinformation about our knittingpiece, in other words \
          a spatial 3d description, where each stitch will be located
        * an evaluation, how fitting the knittingpiece ist, if it will \
          have tension or it will not fit
        * also some minor information, if our knittingpiece is complies \
          with given knittingpatterns

In detail:
        1. A full description of the knitpiece via knittingmanual or a \
           corresponding graph
        2. Spatial(3d location) information about every stitch
        3. in which lines the knitpiece has tension or is loose
        4. if the graph corresponds to a knittinpattern.

In the datagraph this information will be saved within :py:class:`strickgraph_container` (1), :py:class:`clothfactory_parts.strickgraph_spatialdata` (2), \
:py:class:`clothfactory_parts.strickgraph_property_relaxed` (3) annd \
:py:class:`clothfactory_parts.strickgraph_property_plainknit` (4)


Informationinput
----------------

All the static information must be given at the start. So we need all the 
static datagraph nodes:

.. code::

        tmp = datagraph()
        tmp.add_node( "mesh", ply_surface )
        tmp.add_node( "maptomesh", ply_2dmap )
        tmp.add_node( "stitchinfo", strickgraph_stitchdata )
        tmp.add_edge( "maptomesh", "mesh", map_to_mesh )

The information must be initialized, as described in the documentation of
:py:mod:`datagraph_factory`:

.. code::

        [...]
        from createcloth.stitchinfo import basic_stitchdata
        tmp["stitchinfo"] = strickgraph_stitchdata( basic_stitchdata, \
                                          "knit", "yarnover", "bindoff" )
        filepath = "data/surfmap.ply"
        tmpsurf = ply_surface.load_from( filepath )
        tmp["mesh"] = tmpsurf

With this information we want to create a knittingpiece, which is plainknit
and is in a fitting (relaxed) state. Relaxed means no tension and loose parts:

.. code::

        [...]
        tmp.add_node( "strickgraph", strickgraph_container )

        tmp.add_node( "spat", strickgraph_spatialdata )
        tmp.add_edge( "strickgraph", "spat", stitchposition )

        tmp.add_node( "isrelaxed" , strickgraph_property_relaxed )
        tmp.add_edge( "strickgraph", "isrelaxed", \
                        springs_of_strickgraph_are_relaxed )

        tmp.add_node( "isplainknit", strickgraph_property_plainknit )
        tmp.add_edge( "strickgraph", "isplainknit", strickgraph_isplainknit )

A complete datagraph-construction as seen in test_clothfactoryparts:

.. code::

        tmp = datagraph()

        tmp.add_node( "mesh", ply_surface )
        tmp.add_node( "maptomesh", ply_2dmap )
        tmp.add_node( "strickgraph", strickgraph_container )
        tmp.add_node( "spat", strickgraph_spatialdata )
        tmp.add_edge( "strickgraph", "spat", stitchposition )
        tmp.add_edge( "maptomesh", "mesh", map_to_mesh )
        tmp.add_edge( "strickgraph", "mesh", strickgraph_fit_to_mesh )
        tmp.add_edge( "maptomesh", "strickgraph", physics.map_for_strickgraph )
        tmp.add_node( "isrelaxed" , strickgraph_property_relaxed )
        tmp.add_node( "isplainknit", strickgraph_property_plainknit )
        tmp.add_node( "stitchinfo", strickgraph_stitchdata )
        tmp.add_edge( "stitchinfo", "mesh", use_stitchdata_for_construction )
        tmp.add_edge( "strickgraph", "isrelaxed", \
                        springs_of_strickgraph_are_relaxed )
        tmp.add_edge( "strickgraph", "isplainknit", strickgraph_isplainknit )


        from createcloth.stitchinfo import basic_stitchdata
        tmp["stitchinfo"] = strickgraph_stitchdata( basic_stitchdata, \
                                          "knit", "yarnover", "bindoff" )
        filepath = "data/surfmap.ply"
        tmpsurf = ply_surface.load_from( filepath )
        tmp["mesh"] = tmpsurf

Automatic completion of data
----------------------------

To generate our knitting piece from the given information, we have to load \
the given :py:class:`clothfactoy_leafs` from :py:mod:`clothfactory_parts`, 
and let the algorithm magic of datagraph_factory generate our knitting_piece.

As described in the documentation of :py:mod:`datagraph_factory`, to 
complete the daatagraph we have to load the needed factory_leafs:

.. code::

   somethingsomething

With the now generated flowgraph, we can complete our datagraph as \
described in detail in :py:mod:`datagraph_factory`:

.. code::

   from datagraph_factory import DataRescueException, complete_datagraph
   try:
       tmp = complete_datagraph( flowgraph, tmp )
   [...]

Now we can now extract the information from the :py:class:`datagraph<datagraph_factory.datagraph>`:

.. code::

   [...]
   except DataRescueException as err:
       datarescue: function #for description see below
       datarescue( err )
       raise err
   # just for info:
   tmp["strickgraph"]: clothfactory_leaf.strickgraph_container
   generated_strickgraph: createcloth.strickgraph.strickgraph

   generated_strickgraph = tmp["strickgraph"].strickgraph
   stinfo = createcloth.stitchinfo.basic_stitchdata

   print( generated_strickgraph.to_manual( stinfo ) )

If the algorithm fails we can extract the available data with the a function,
we call it here :py:func:`datarescue`. See for exact instruction in
documentation :py:mod:`datagraph_factory` or in the testmethod 
:py:mod:`clothfactory_parts.test_clothfactory_parts`.

.. code::

   with tempfile.TemporaryDirectory() as tmpdir:
       save_graph( tmp, tmpdir, [ meshthings, physics, plainknit, strickgraph] )


Reference for programs
----------------------

.. program:: create_directory_strickcompleter

   ASDF myprogram AAAAAAAAAAA

.. option:: -d <directory>

   wait what is this???

.. automodule:: clothfactory_parts.programs.create_directory_strickcompleter
   :members:

