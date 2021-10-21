Identify Strickgraph as plainknit
---------------------------------

Use this function: :py:function:`isplain<createcloth.plainknit.method_isplain.isplain_strickgraph>` for identification.


Create Strickgraph from Linetypes
---------------------------------

Here is a codebook example on howto create a strickgraph from linetypes

.. code::

        def create_graph_from_linetypes( linetypes, upedges, startside="right" ):
            if startside == "right":
                sides = ("right", "left")
            else:
                sides = ("left", "right")
            downedges = [ None, *upedges ]
            upedges = [ *upedges, None ]
            iline = range(len(downedges))
            allinfo = zip( linetypes, downedges, upedges, iline )

            graph_man = [ s.create_example_row( down, up, side=sides[i%2] ) \
                                        for s, down, up, i in allinfo ]

            graph = strickgraph.from_manual( graph_man, glstinfo, \
                                        manual_type="machine")
            return graph

This correspondes also to :py:method:`createcloth.plainknit.test.TestMeshhandlerMethods.test_createverbesserer`
