from datagraph_factory.datagraph import datagraph
import itertools
import networkx as netx
from datagraph_factory.processes import factory_leaf
from .plyford_mesh_handler import stitchposition
from .improving.add_column_both_sides import check_single_line as isplainline
from .strickgraph_datatypes import \
        strickgraph_container, \
        strickgraph_spatialdata, \
        strickgraph_property_relaxed, \
        springs_of_strickgraph_are_relaxed, \
        springs_of_strickgraph_have_tension, \
        springs_of_strickgraph_have_pressure

from .plainknit import \
        strickgraph_property_plainknit, \
        strickgraph_isplainknit, \
        strickgraph_isnotplainknit

tmp = datagraph()
tmp.add_node( "mystrick", strickgraph_container )
tmp.add_node( "positions", strickgraph_spatialdata )
tmp.add_edge( "mystrick", "positions", stitchposition )
prestatus = tmp.copy()
tmp.add_node( "isrelaxed", strickgraph_property_relaxed )
tmp.add_node( "havetension", strickgraph_property_relaxed )
tmp.add_node( "havepressure", strickgraph_property_relaxed )
tmp.add_edge( "mystrick", "isrelaxed", springs_of_strickgraph_are_relaxed )
tmp.add_edge( "mystrick", "havetension", \
                            springs_of_strickgraph_have_tension )
tmp.add_edge( "mystrick", "havepressure", \
                            springs_of_strickgraph_have_pressure )
poststatus = tmp.copy()
del( tmp )
def call_function( mystrick, positions ):
    x = positions.xposition
    y = positions.yposition
    z = positions.zposition
    l = positions.edgelengthdict
    lcalm = positions.calmlengthdict

    rows = mystrick.strickgraph.get_rows()
    qwer = lambda q: list(q)[0:5] + list(q)[-6:-1]
    asdf = lambda row: qwer(itertools.zip_longest( row[0:-2], row[1:-1] ))

    valueable_edges = [ asdf( row ) for row in rows ]
    haspressure, hastension = set(), set()
    for i in range(len(valueable_edges)):
        myedges = list( valueable_edges[i] )
        q = 0
        for e1, e2 in myedges:
            edge = frozenset(( e1, e2 ))
            q += l[edge]-0.1
            if l[edge]-0.1 > 0.02:
                hastension.add(i)
            elif l[edge]-0.1 < -0.02:
                haspressure.add(i)
        print(i, q, len(rows[i]))
    print( f"\npress: {haspressure}, \n\n tens: {hastension}\n")
    if haspressure and hastension:
        return { "havetension": strickgraph_property_relaxed( \
                                                    tensionrows=hastension), \
                "havepressure": strickgraph_property_relaxed( \
                                                    pressurerows=haspressure) }
    elif haspressure:
        return { "havepressure": strickgraph_property_relaxed( \
                                                    pressurerows=haspressure) }
    elif hastension:
        return { "havetension": strickgraph_property_relaxed( \
                                                    tensionrows=hastension) }
    else:
        return{ "isrelaxed": strickgraph_property_relaxed() }
test_if_strickgraph_isrelaxed = factory_leaf( prestatus, poststatus, \
                                call_function, name=__name__+"test relax" )
del( prestatus, poststatus, call_function )
