Strickgraph
***********

Description
===========

Description of knitpieces in manualform
---------------------------------------

Here we will introduce an implementation of a knitting piece via software, 
with all capabilities, you would ever desire:) 

The implementation will be called 
:py:class:`Strickgraph<createcloth.strickgraph.strickgraph>` and a full 
reference is listed at the end of this section.

First we will introduce, the common representations of knitpieces. Also we 
will give to every common representation a translation-howto for the
implementation :py:class:`Strickgraph<createcloth.strickgraph.strickgraph>`.
The common representation is as knitting manuals in different styles:

        * hand knitting charts (see eg `stitch-maps.com`_ )
        * machine matrices


.. _stitch-maps.com: https://stitch-maps.com

Machine knitting matrices
~~~~~~~~~~~~~~~~~~~~~~~~~

.. todo:: 

   implement machine matrice thingies

Hand knitting charts
~~~~~~~~~~~~~~~~~~~~

Hand knitting charts are used for row to row implementations, so that
you as knitter can knit-as-read.

The implementation 
:py:class:`Strickgraph<createcloth.strickgraph.strickgraph>` has two
different kinds of knit charts, that look similar.

First we have a knit-as-read manual, which means in contrast, that the
first stitch you make in each row, is the leftmost stitch in the manual.
This manual describes a knitpiece via lines of stitches, and you just have
to knit in parallel, to what you read, eg:

.. code::

   4bindoff
   3knit 1k2tog
   5yarnover

Here you start your knitpiece with 5 stitches, knit a right-knit stitches 
in the next row (also 3), ending with a stitch, that tightens two stitches 
to one. The third row is the last, where you finish your
knitpiece, with 4 bindoff-stitches. Note that the read direction is from 
bottom to top.

We can create an virtual object reperenting this knitpiece via
:py:meth:`Strickgraph from manual<createcloth.strickgraph.strickgraph.from_manual>`.

.. code::

   from createcloth.stitchinfo import basic_stitchinfo
   manual = "4bo\n3k 1k2tog\n5yo"
   knitpiece = strickgraph.from_manual( manual, basic_stitchinfo, \
                                        manual_type="hand" )

Note, that we need a 
:py:class:`translationpiece for every stitch<createcloth.stitchinfo>`. 
In this package a 
:py:class:`basic translation<createcloth.stitchinfo.basic_stitchinfo>` 
is given and can be loaded as seen above. It translates our stitchnames
(eg 'yarnover') and the used symbols (eg 'yo'), from our manual for 
the strickgraph.

.. todo::

   more information about knittingmanuals, charts or whatever possible with 
   references instead of here described

We have different things we must discuss here, as startingside 'right' or 
'left'. And also the difference of, written-as-you-knit(handknitting) and
written-as-you-see(machineknitting) must be further described.

.. todo::

   i plan on using for handknitting-terms and machine-knitting terms conatiners
   (see collections.abc.Container for more information). So this might 
   change in the future

Abstract strickgraph generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Also you can generate a strickgraph with the help of a `graph<networkx.Graph>`.
This is a more abstract generation, but represents the innerstate of our 
strickgraph.

To give a short description of graphs. A graph is a set of nodes, which 
can represent anything (in our case, each respresents a single stitch).
Those nodes have a, again, a so called edge. Edges can represent any 
kind of relation between 2 nodes. In our case, they represent, that 
the 2 stitches are connected via thread. 

.. image:: ../stitchchartasgraph.jpg
   :height: 6cm


For further information you could look at internet eg: `wikipedia`_

.. _wikipedia: https://en.wikipedia.org/wiki/Graph_(discrete_mathematics)

We can generate our strickgraph via a basic graph, but we need not only the
graph(*graph*) itself but also we must specify the first row(*firstrow*)
of the strickgraph.
The first row represents in terms of a knitchart our first knitted line. 
also we need general information(*basic_stitchdata*) about our knitpiece. Eg:

.. code::

        from createcloth.stitchinfo import basic_stitchdata
        import networkx
        graph = networkx.grid_2d_graph( 4,4 )
        firstrow = [ x for x in graph.nodes() if x[0] == 0 ]

        asd = strickgraph.from_gridgraph( graph, firstrow, basic_stitchdata )

.. todo::

   Strickgraphgeneration from graphs might fail because of various reasons.
   It might be nice to have a what-has-gone-wrong guide somewhere.

Handling strickgraphs
=====================

.. todo::

   I plan on making a abstract class for graphs, mainly because of 
   graphalteration. This abstract class then will be used for strickgraphs.
   Eventual more methods that are abstractable will then be listed here.


all nodes and information
~~~~~~~~~~~~~~~~~~~~~~~~~

As mentioned the strickgraph is at its core a graph. This means every 
stitch is represented via a node and every connection between stitch is 
represented via an edge.

Acces to nodes:

.. code::

   strickgraph.get_nodes
   strickgraph.get_nodeattributes
   strickgraph.get_edges_with_labels
   strickgraph.get_nodeattr_stitchtype
   strickgraph.get_nodeattr_side
   strickgraph.get_nodeattr_alternativestitchtype

Rows
~~~~

We can get get rows via :py:meth:`get_rows`

.. code::

        strickgraph.get_rows

border
~~~~~~

We can get a border of the strickgraph. The border should be the outer ost stitch
of the strickgraph. That means, if a line (not the last one) just begins with 
ending some columns(eg per bindoffs) you have those stitches as border
of the knitpiece.

Currently the border is just the first and last row, and every stitch at 
the start and end of each row.


sidemargins
~~~~~~~~~~~

The first x-stitches and x-last stitches of each row.

.. code::

        strickgraph.get_sidemargins
        strickgraph.get_sidemargins_indices

special stitches
~~~~~~~~~~~~~~~~

.. code::

        strickgraph.get_startstitch
        strickgraph.get_endstitch
        strickgraph.get_nodes_near_nodes
        strickgraph.get_nodes
        strickgraph.get_next_node_to



clothfactory-parts
==================

To the Strickgraph coresponding factoryleafs are 
        * :py:class:`clothfactory_parts.strickgraph.strickgraph.datatypes.strickgraph_container`
        * :py:data:`clothfactory_parts.plainknit.factory_leaf.relax_tension`
        * :py:data:`clothfactory_parts.plainknit.factory_leaf.relax_pressure`


References
==========


.. autoclass:: createcloth.strickgraph.strickgraph_base.strickgraph
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: createcloth.strickgraph.strickgraph_fromgrid.strick_fromgrid
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: createcloth.strickgraph.strickgraph_base.strick_compare
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: createcloth.strickgraph.strickgraph_base.alternative_stitchtype_support
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: createcloth.strickgraph.strickgraph_toknitmanual.strick_manualhelper
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

.. autoclass:: createcloth.strickgraph.datacontainer.strick_datacontainer
   :members:
   :undoc-members:
   :show-inheritance:
