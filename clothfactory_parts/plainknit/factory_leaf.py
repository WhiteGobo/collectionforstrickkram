from datagraph_factory import datagraph, factory_leaf
from .. import strickgraph
from .factory_datatype import strickgraph_property_plainknit, \
        strickgraph_isplainknit, \
        strickgraph_isnotplainknit
from .. import meshthings
from .widthchanger import add_columns, remove_columns, \
                            failedOperation, extend_columns, inset_columns

import networkx as netx
from .plain_identifier import isplain, notplainException, \
                            getplainknit_linetypes


def create_datagraphs():
    tmp = datagraph()
    tmp.add_node( "mystrick", strickgraph.strickgraph_container )
    prestatus = tmp.copy()
    tmp.add_node( "isplainknit", strickgraph_property_plainknit )
    tmp.add_node( "isnotplainknit", strickgraph_property_plainknit )
    tmp.add_edge( "mystrick", "isplainknit", strickgraph_isplainknit )
    tmp.add_edge( "mystrick", "isnotplainknit", strickgraph_isnotplainknit )
    poststatus = tmp.copy()
    return prestatus, poststatus
def call_function( mystrick ):
    mystrickgraph = mystrick.strickgraph

    #if rows_are_plainstrick( mystrickgraph.get_rows(), stitchtype ):
    #if a:
    try:
        linetypes = getplainknit_linetypes( mystrickgraph )
        return { "isplainknit": strickgraph_property_plainknit( linetypes ) }
    except notplainException as err:
        print( err.args )
        return { "isnotplainknit": strickgraph_property_plainknit( err.args ) }
    if isplain( mystrickgraph ):
        return { "isplainknit": strickgraph_property_plainknit() }
    else:
        return { "isnotplainknit": strickgraph_property_plainknit() }
test_if_strickgraph_is_plainknit = factory_leaf( create_datagraphs, \
                                        call_function, \
                                        name =__name__+"test plainknit" )
del( create_datagraphs )



def create_datagraphs():
    tmp = datagraph()
    tmp.add_node( "mystrickgraph", strickgraph.strickgraph_container )
    tmp.add_node( "mymesh", meshthings.ply_surface )
    tmp.add_node( "isrelaxed", strickgraph.strickgraph_property_relaxed )
    tmp.add_node( "isplainknit", strickgraph_property_plainknit )
    tmp.add_edge( "mystrickgraph", "isrelaxed", \
                    strickgraph.springs_of_strickgraph_have_tension )
    tmp.add_edge( "mystrickgraph", "isplainknit", strickgraph_isplainknit )
    tmp.add_edge( "mystrickgraph", "mymesh", meshthings.strickgraph_fit_to_mesh )
    prestatus = tmp.copy()
    tmp.remove_node( "mystrickgraph" )
    tmp.remove_node( "isplainknit" )
    tmp.remove_node( "isrelaxed" )
    tmp.add_node( "newstrickgraph", strickgraph.strickgraph_container )
    tmp.add_node( "new_isplainknit", strickgraph_property_plainknit )
    tmp.add_edge( "newstrickgraph", "new_isplainknit", strickgraph_isplainknit )
    tmp.add_edge( "newstrickgraph", "mymesh", meshthings.strickgraph_fit_to_mesh )
    poststatus = tmp.copy()
    return prestatus, poststatus
def call_function( isrelaxed, isplainknit, mystrickgraph, mymesh ):
    tobeextendedrows = isrelaxed.tensionrows
    tmpstrickgraph = mystrickgraph.strickgraph
    rows = tmpstrickgraph.get_rows()
    if len(rows)-1 in tobeextendedrows:
        tobeextendedrows.add( len(rows)-2 )
    if 0 in tobeextendedrows:
        tobeextendedrows.add( 1 )
    try:
        add_columns( tmpstrickgraph, tobeextendedrows )
    except failedOperation as err:
        extend_columns( tmpstrickgraph, tobeextendedrows )
    return { "newstrickgraph": strickgraph.strickgraph_container( tmpstrickgraph ) }
relax_tension = factory_leaf( create_datagraphs, call_function, \
                            name = __name__+".improve strickgraph tension" )


def create_datagraphs():
    tmp = datagraph()
    tmp.add_node( "mystrickgraph", strickgraph.strickgraph_container )
    tmp.add_node( "mymesh", meshthings.ply_surface )
    tmp.add_node( "isrelaxed", strickgraph.strickgraph_property_relaxed )
    tmp.add_node( "isplainknit", strickgraph_property_plainknit )
    tmp.add_edge( "mystrickgraph", "isrelaxed", \
                    strickgraph.springs_of_strickgraph_have_pressure )
    tmp.add_edge( "mystrickgraph", "isplainknit", strickgraph_isplainknit )
    tmp.add_edge( "mystrickgraph", "mymesh", meshthings.strickgraph_fit_to_mesh )
    prestatus = tmp.copy()
    tmp.remove_node( "mystrickgraph" )
    tmp.remove_node( "isplainknit" )
    tmp.remove_node( "isrelaxed" )
    tmp.add_node( "newstrickgraph", strickgraph.strickgraph_container )
    tmp.add_node( "new_isplainknit", strickgraph_property_plainknit )
    tmp.add_edge( "newstrickgraph", "new_isplainknit", strickgraph_isplainknit )
    tmp.add_edge( "newstrickgraph", "mymesh", meshthings.strickgraph_fit_to_mesh )
    poststatus = tmp.copy()
    return prestatus, poststatus
def call_function( isrelaxed, isplainknit, mystrickgraph, mymesh ):
    tobeshortenedrows = isrelaxed.pressurerows
    tmpstrickgraph = mystrickgraph.strickgraph
    rows = tmpstrickgraph.get_rows()
    if len(rows)-1 in tobeshortenedrows:
        tobeshortenedrows.add( len(rows)-2 )
    if 0 in tobeshortenedrows:
        tobeshortenedrows.add( 1 )
    #newstrickgraph = mystrickgraph.copy()
    try:
        remove_columns( tmpstrickgraph, tobeshortenedrows )
    except failedOperation as err:
        inset_columns( tmpstrickgraph, tobeshortenedrows )
    return { "newstrickgraph": strickgraph.strickgraph_container( tmpstrickgraph ) }
relax_pressure = factory_leaf( create_datagraphs, call_function, \
                            name = __name__ + ".improvestrickgraph pressure")
