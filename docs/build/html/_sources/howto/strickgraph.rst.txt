How to handle Strickgraphs
==========================

Printing Strickgraphs
---------------------

The easiest way to look at Strickgraphs is via a manual:
.. code::

    ... mystrickgraph: createcloth.strickgraph.strickgraph
    ... stitchinfo: createcloth.strickgraph.stitchinfo
    >>> print( mystrickgraph.to_manual( stitchinfo ) )
    ... 6yo
    ... 6k
    ... 6k
    ... 6bo
    >>> print( { symbol:stitch 
                for symbol, stitch in stitchinfo.asdf().items()
                if symbol in ( 'yo', 'k', 'bo' )} )
    ... { 'yo': 'yarnover', 'k': 'knit', 'bo': 'bindoff' }

You can directly see, that our Strickgraph consist of four rows each with 
6 stitches. The first consists of yarnover-, the last bindoff- and the middle 
of knit-stitches.

To have complete information you also need the startside:
.. code::

    ... mystrickgraph: createcloth.strickgraph.strickgraph
    >>> print( mystrickgraph.get_startside() )
    ... right

Valid startsides are "right" and "left".




Howto create a strickalterator
------------------------------

The most solid solution is to get valid input-output scenarios of an alteration
and create from them the desired alterations.

.. code::

   ... inmanual  == "6yo\n1k 1kmark 1k2tog 2k\n1k 1k2tog 2k\n4bo"
   ... outmanual == "6yo\n1k 1kmark 2k 2bo\n4k\n4bo"
   >>> alter = strickalterator.from_manuals( inmanual, outmanual, stitchinfo )

For use of multiple senarios at the same time see [1].

This alterator holds only one in-out-scenario. For holding an array of possible
scenarios the class multi_strickverbesserer will be used instead. See [1] for this.

After creation the strickalterator can be used on every fitting Strickgraph, when given the correct startposition:

.. code::

   ... inmanual  == "6yo\n2k 1k2tog 2k\n1k 1k2tog 2k\n4bo"
   >>> mygraph = strickgraph.from_manual( inmanual )
   >>> alter = strickalterator.from_manuals( inmanual, outmanual, stitchinfo )
   >>> alter.replace_in_graph( mygraph, (1,1) )
   >>> print( mygraph.to_manual( stitchinfo ) )
   ... 6yo
   ... 4k 2bo
   ... 4k
   ... 4bo
