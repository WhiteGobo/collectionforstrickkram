import itertools
from .. import strickgraph
from datagraph_factory import datatype, factory_leaf, datagraph

from createcloth.physicalhelper import relaxedgelength_to_strickgraph, \
                                        singleedge_length, \
                                        standardthreadinfo as mythreadinfo

import logging
logger = logging.getLogger( __name__ )

class test_if_strickgraph_isrelaxed( factory_leaf ):
    def generate_datagraphs( self ):
        tmp = datagraph()
        tmp.add_node( "mystrick", strickgraph.strickgraph_container )
        tmp.add_node( "positions", strickgraph.strickgraph_spatialdata )
        tmp.add_edge( "mystrick", "positions", strickgraph.stitchposition )
        prestatus = tmp.copy()
        tmp.add_node( "isrelaxed", strickgraph.strickgraph_property_relaxed )
        tmp.add_node( "havetension", strickgraph.strickgraph_property_relaxed )
        tmp.add_node( "havepressure", strickgraph.strickgraph_property_relaxed )
        tmp.add_edge( "mystrick", "isrelaxed", \
                                strickgraph.springs_of_strickgraph_are_relaxed )
        tmp.add_edge( "mystrick", "havetension", \
                                strickgraph.springs_of_strickgraph_have_tension )
        tmp.add_edge( "mystrick", "havepressure", \
                                strickgraph.springs_of_strickgraph_have_pressure )
        poststatus = tmp.copy()
        return prestatus, poststatus
    def call_function( self, mystrick, positions ):
        """

        :todo: revisited the adding of the lastrow to haspressure lines
        """
        x = positions.xposition
        y = positions.yposition
        z = positions.zposition
        l = positions.edgelengthdict
        assert set(mystrick.strickgraph.get_nodes()) == set(x.keys()), "adf"
        edge_to_calmlength = positions.calmlengthdict
        #lengthgraph = relaxedgelength_to_strickgraph( mystrick.strickgraph )
        ##edge_to_calmlength = lambda e: lengthgraph[e]["calmlength"]
        #edge_to_calmlength = netx.get_edge_attributes( lengthgraph, "calmlength" )
        #edge_to_calmlength = { frozenset(key): value \
        #                        for key, value in edge_to_calmlength.items() }
        lengthforextrastitch = singleedge_length( "knit", "knit", "next", \
                                                    mythreadinfo )

        rows = mystrick.strickgraph.get_rows()
        from createcloth.stitchinfo import basic_stitchdata as stinfo
        print( mystrick.strickgraph.to_manual( stinfo).replace("\n", ";" ) )
        #qwer = lambda q: list(q)[0:5] + list(q)[-6:-1]
        #asdf = lambda row: qwer( zip( row[0:-2], row[1:-1] ))
        vertline_to_edges = lambda verts: list( zip( verts[:-2], verts[1:] ) )

        to_rownumber = {}
        for i, row in enumerate( rows ):
            for v in row:
                to_rownumber[v] = i
        same_row = lambda v1, v2: to_rownumber[v1] == to_rownumber[v2]
        allready_visited = set()
        rowlength = [0.0] * len(rows)
        row_overlength = [0.0] * len(rows)
        var_optimal_length = [0.0] * len(rows)
        from numpy.linalg import norm
        for v1, v2 in ( (v1, v2) for v1, v2 in positions.edges if same_row(v1, v2)):
            if frozenset((v1, v2)) not in allready_visited:
                allready_visited.add( frozenset((v1, v2)) )
                i = to_rownumber[ v1 ]
                rowlength[i] += positions.edgelengthdict[ (v1, v2) ]
                row_overlength[i] += positions.edgelengthdict[ (v1, v2) ] \
                                    - positions.calmlengthdict[ (v1, v2) ]
                var_optimal_length[i] += (positions.edgelengthdict[ (v1, v2) ] \
                                    - positions.calmlengthdict[ (v1, v2) ])**2

        LENIENCE = 2.5
        haspressure, hastension = set(), set()
        for i, row in enumerate( rows ):
            length_for_extrastitch_per_stitch = lengthforextrastitch
            if row_overlength[i] > LENIENCE * lengthforextrastitch:
                hastension.add(i)
            elif row_overlength[i] < -LENIENCE * lengthforextrastitch:
                haspressure.add(i)

        lastrow_index = len( rows )-1
        if lastrow_index not in haspressure and lastrow_index-1 in haspressure:
            haspressure.add( lastrow_index )

        logger.debug( f"brubru \ntension: {hastension}\npressure: {haspressure}" )
        if haspressure and hastension:
            rval = { "havetension": strickgraph.strickgraph_property_relaxed( \
                                                        tensionrows=hastension), \
                    "havepressure": strickgraph.strickgraph_property_relaxed( \
                                                        pressurerows=haspressure) }
            print( rval )
            return rval
        elif haspressure:
            return { "havepressure": strickgraph.strickgraph_property_relaxed( \
                                                        pressurerows=haspressure) }
        elif hastension:
            return { "havetension": strickgraph.strickgraph_property_relaxed( \
                                                        tensionrows=hastension) }
        else:
            return{ "isrelaxed": strickgraph.strickgraph_property_relaxed() }
#test_if_strickgraph_isrelaxed:factory_leaf = factory_leaf( _create_datagraphs, \
        #                                _call_function, name=__name__+"test relax" )
"""Tests if strickgraph is relaxed.
Uses :py:class:`clothfactory.strickgraph.strickgraph_datatypes.strickgraph_container` and 
:py:class:`clothfactory.strickgraph.strickgraph_datatypes.strickgraph_spatialdata` to create :py:class:`clothfactory_parts.strickgraph.strickgraph_datatypes.strickgraph_property_relaxed`

:todo: overhaul description
"""
