import itertools
import networkx as netx
from .. import strickgraph
from datagraph_factory import datatype, factory_leaf, datagraph

from createcloth.physicalhelper import relaxedgelength_to_strickgraph, \
                                        singleedge_length, \
                                        standardthreadinfo as mythreadinfo

def create_datagraphs():
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
def call_function( mystrick, positions ):
    x = positions.xposition
    y = positions.yposition
    z = positions.zposition
    l = positions.edgelengthdict
    lcalm = positions.calmlengthdict
    lengthgraph = relaxedgelength_to_strickgraph( mystrick.strickgraph )
    #edge_to_calmlength = lambda e: lengthgraph[e]["calmlength"]
    edge_to_calmlength = netx.get_edge_attributes( lengthgraph, "calmlength" )
    edge_to_calmlength = { frozenset(key): value \
                            for key, value in edge_to_calmlength.items() }
    lengthforextrastitch = singleedge_length( "knit", "knit", "next", \
                                                mythreadinfo )

    rows = mystrick.strickgraph.get_rows()
    qwer = lambda q: list(q)[0:5] + list(q)[-6:-1]
    asdf = lambda row: qwer(itertools.zip_longest( row[0:-2], row[1:-1] ))

    valueable_edges = [ asdf( row ) for row in rows ]
    haspressure, hastension = set(), set()
    for i in range(len(valueable_edges)):
        myedges = list( valueable_edges[i] )
        overlength = 0.0 #total length - sum of all length of edges
        for e1, e2 in myedges:
            edge = frozenset(( e1, e2 ))
            overlength += l[edge] - edge_to_calmlength[ edge ]
            #if l[edge]-0.1 > lengthforextrastitch:
            #    hastension.add(i)
            #elif l[edge]-0.1 < -lengthforextrastitch:
            #    haspressure.add(i)
        if overlength > lengthforextrastitch:
            hastension.add(i)
        elif overlength < -lengthforextrastitch:
            haspressure.add(i)
    print( f"\npress: {haspressure}, \n\n tens: {hastension}\n")
    if haspressure and hastension:
        return { "havetension": strickgraph.strickgraph_property_relaxed( \
                                                    tensionrows=hastension), \
                "havepressure": strickgraph.strickgraph_property_relaxed( \
                                                    pressurerows=haspressure) }
    elif haspressure:
        return { "havepressure": strickgraph.strickgraph_property_relaxed( \
                                                    pressurerows=haspressure) }
    elif hastension:
        return { "havetension": strickgraph.strickgraph_property_relaxed( \
                                                    tensionrows=hastension) }
    else:
        return{ "isrelaxed": strickgraph.strickgraph_property_relaxed() }
test_if_strickgraph_isrelaxed = factory_leaf( create_datagraphs, \
                                call_function, name=__name__+"test relax" )
