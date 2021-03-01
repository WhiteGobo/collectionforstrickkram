from datagraph_factory.datagraph import datagraph
from datagraph_factory.processes import factory_leaf
from ..strickgraph_datatypes import strickgraph_container
from .factory_datatype import strickgraph_property_plainknit, \
        strickgraph_isplainknit, \
        strickgraph_isnotplainknit
from ..strickgraph_datatypes import strickgraph_property_relaxed, \
        springs_of_strickgraph_have_tension, \
        springs_of_strickgraph_have_pressure
from ..plyford_mesh_handler import mesh_pymesh2, \
        strickgraph_fit_to_mesh
from .widthchanger import add_columns, remove_columns, failedOperation

import networkx as netx
from .plain_identifier import isplain



tmp = datagraph()
tmp.add_node( "mystrick", strickgraph_container )
prestatus = tmp.copy()
tmp.add_node( "isplainknit", strickgraph_property_plainknit )
tmp.add_node( "isnotplainknit", strickgraph_property_plainknit )
tmp.add_edge( "mystrick", "isplainknit", strickgraph_isplainknit )
tmp.add_edge( "mystrick", "isnotplainknit", strickgraph_isnotplainknit )
poststatus = tmp.copy()
del( tmp )
def call_function( mystrick ):
    mystrickgraph = mystrick.strickgraph

    #if rows_are_plainstrick( mystrickgraph.get_rows(), stitchtype ):
    #if a:
    if isplain( mystrickgraph ):
        return { "isplainknit": strickgraph_property_plainknit() }
    else:
        raise Exception()
        return { "isnotplainknit": strickgraph_property_plainknit() }
test_if_strickgraph_is_plainknit = factory_leaf( prestatus, poststatus, \
                                        call_function, \
                                        name =__name__+"test plainknit" )
del( prestatus, poststatus, call_function )



tmp = datagraph()
tmp.add_node( "mystrickgraph", strickgraph_container )
tmp.add_node( "mymesh", mesh_pymesh2 )
tmp.add_node( "isrelaxed", strickgraph_property_relaxed )
tmp.add_node( "isplainknit", strickgraph_property_plainknit )
tmp.add_edge( "mystrickgraph", "isrelaxed", \
                springs_of_strickgraph_have_tension )
tmp.add_edge( "mystrickgraph", "isplainknit", strickgraph_isplainknit )
tmp.add_edge( "mystrickgraph", "mymesh", strickgraph_fit_to_mesh )
prestatus = tmp.copy()
tmp.remove_node( "mystrickgraph" )
tmp.remove_node( "isplainknit" )
tmp.remove_node( "isrelaxed" )
tmp.add_node( "newstrickgraph", strickgraph_container )
tmp.add_node( "new_isplainknit", strickgraph_property_plainknit )
tmp.add_edge( "newstrickgraph", "new_isplainknit", strickgraph_isplainknit )
tmp.add_edge( "newstrickgraph", "mymesh", strickgraph_fit_to_mesh )
poststatus = tmp.copy()
del( tmp )
def call_function( isrelaxed, isplainknit, mystrickgraph, mymesh ):
    tobeextendedrows = isrelaxed.tensionrows
    tmpstrickgraph = mystrickgraph.strickgraph
    try:
        add_columns( tmpstrickgraph, tobeextendedrows )
        return { "newstrickgraph": strickgraph_container( tmpstrickgraph ) }
    except failedOperation:
        return None
relax_tension = factory_leaf( prestatus, poststatus, call_function, \
                                name = __name__+".improve strickgraph tension" )
del( prestatus, poststatus, call_function )


tmp = datagraph()
tmp.add_node( "mystrickgraph", strickgraph_container )
tmp.add_node( "mymesh", mesh_pymesh2 )
tmp.add_node( "isrelaxed", strickgraph_property_relaxed )
tmp.add_node( "isplainknit", strickgraph_property_plainknit )
tmp.add_edge( "mystrickgraph", "isrelaxed", \
                springs_of_strickgraph_have_pressure )
tmp.add_edge( "mystrickgraph", "isplainknit", strickgraph_isplainknit )
tmp.add_edge( "mystrickgraph", "mymesh", strickgraph_fit_to_mesh )
prestatus = tmp.copy()
tmp.remove_node( "mystrickgraph" )
tmp.remove_node( "isplainknit" )
tmp.remove_node( "isrelaxed" )
tmp.add_node( "newstrickgraph", strickgraph_container )
tmp.add_node( "new_isplainknit", strickgraph_property_plainknit )
tmp.add_edge( "newstrickgraph", "new_isplainknit", strickgraph_isplainknit )
tmp.add_edge( "newstrickgraph", "mymesh", strickgraph_fit_to_mesh )
poststatus = tmp.copy()
del( tmp )
def call_function( isrelaxed, isplainknit, mystrickgraph, mymesh ):
    tobeshortendrows = isrelaxed.pressurerows
    #newstrickgraph = mystrickgraph.copy()
    tmpstrickgraph = mystrickgraph.strickgraph
    remove_columns( tmpstrickgraph, tobeshortendrows )
    return { "newstrickgraph": strickgraph_container( tmpstrickgraph ) }#, \
            #"new_isplainknit": strickgraph_property_plainknit() }
relax_pressure = factory_leaf( prestatus, poststatus, call_function, \
                                name = __name__ + "improvestrickgraph pressure")
del( prestatus, poststatus, call_function )

