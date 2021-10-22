"""This module provides factoryleafs for reworking strickgraph, if its plainknit"""
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
from typing import Union, Dict

from createcloth import plainknit as pk
from createcloth.stitchinfo import basic_stitchdata as stinfo

import logging
logger = logging.getLogger( __name__ )


def _sip_create_datagraphs():
    tmp = datagraph()
    tmp.add_node( "mystrick", strickgraph.strickgraph_container )
    prestatus = tmp.copy()
    tmp.add_node( "isplainknit", strickgraph_property_plainknit )
    tmp.add_node( "isnotplainknit", strickgraph_property_plainknit )
    tmp.add_edge( "mystrick", "isplainknit", strickgraph_isplainknit )
    tmp.add_edge( "mystrick", "isnotplainknit", strickgraph_isnotplainknit )
    poststatus = tmp.copy()
    return prestatus, poststatus
_sip_call_rtype = Union[ strickgraph_property_plainknit, \
                        strickgraph_property_plainknit ]
def _sip_call_function( mystrick: strickgraph.strickgraph_container ) \
                        -> Dict[ str, _sip_call_rtype ]:
    """Tests if Strickgraph corresponds to plainknit

    :todo: use method from createcloth.plainknit to identify
    :return: data[isplainknit'] if strick is plain
            else data[isnotplainknit']
    """
    mystrickgraph = mystrick.strickgraph

    #if rows_are_plainstrick( mystrickgraph.get_rows(), stitchtype ):
    #if a:
    try:
        linetypes = getplainknit_linetypes( mystrickgraph )
        return { "isplainknit": strickgraph_property_plainknit( linetypes ) }
    except notplainException as err:
        return { "isnotplainknit": strickgraph_property_plainknit( err.args ) }
    if isplain( mystrickgraph ):
        return { "isplainknit": strickgraph_property_plainknit() }
    else:
        return { "isnotplainknit": strickgraph_property_plainknit() }

test_if_strickgraph_is_plainknit: factory_leaf = factory_leaf( \
                                        _sip_create_datagraphs, \
                                        _sip_call_function, \
                                        name =__name__+"test plainknit" )
"""Factoryleaf for creation of datagraphleaf 'isplainknit'

.. autofunction:: _sip_create_datagraphs
.. autofunction:: _sip_call_function
"""



def _rt_create_datagraphs():
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
_rt_call_rtype = Union[ strickgraph.strickgraph_container, \
                        strickgraph_property_plainknit ]
def _rt_call_function( isrelaxed: strickgraph.strickgraph_property_relaxed, \
                        isplainknit: strickgraph_property_plainknit, \
                        mystrickgraph: strickgraph.strickgraph_container, \
                        mymesh:meshthings.ply_surface ) \
                        -> Dict[ str, _rt_call_rtype ]:
    tobeextendedrows = isrelaxed.tensionrows
    tmpstrickgraph = mystrickgraph.strickgraph
    rows = tmpstrickgraph.get_rows()
    if len(rows)-1 in tobeextendedrows:
        tobeextendedrows.add( len(rows)-2 )
    if 0 in tobeextendedrows:
        tobeextendedrows.add( 1 )

    tobeadded_rows = get_longest_series( tobeextendedrows )
    logger.debug( f"add lines {tobeadded_rows} from {tobeextendedrows}")
    for i in sorted( tobeextendedrows ):
        pk.plainknit_increaser.replace_in_graph( tmpstrickgraph, i )
    logger.debug( tmpstrickgraph.to_manual( stinfo ) )
    return { "newstrickgraph": strickgraph.strickgraph_container( tmpstrickgraph ) }
relax_tension:factory_leaf = factory_leaf( _rt_create_datagraphs, _rt_call_function, \
                            name = __name__+".improve strickgraph tension" )
"""factoryleaf for relaxing tension in line via insertion

.. autofunction:: _rt_create_datagraphs
.. autofunction:: _rt_call_function
"""


def _rp_create_datagraphs():
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
_rp_call_rtype = Union[ strickgraph.strickgraph_container,\
                        strickgraph_property_plainknit, \
                        ]
def _rp_call_function( isrelaxed: strickgraph.strickgraph_property_relaxed, \
                    isplainknit: strickgraph_property_plainknit, \
                    mystrickgraph: strickgraph.strickgraph_container, \
                    mymesh: meshthings.ply_surface )\
                    ->Dict[ str, _rp_call_rtype ]:
    tobeshortenedrows = isrelaxed.pressurerows
    tmpstrickgraph = mystrickgraph.strickgraph
    rows = tmpstrickgraph.get_rows()
    if len(rows)-1 in tobeshortenedrows:
        tobeshortenedrows.add( len(rows)-2 )
    if 0 in tobeshortenedrows:
        tobeshortenedrows.add( 1 )
    #newstrickgraph = mystrickgraph.copy()

    toberemoved_rows = get_longest_series( tobeshortenedrows )
    logger.debug( f"remove lines {toberemoved_rows} from {tobeshortenedrows}")
    for i in sorted( tobeshortenedrows, reverse=True): #problems with decrease last row
        pk.plainknit_decreaser.replace_in_graph( tmpstrickgraph, i )
    logger.debug( tmpstrickgraph.to_manual( stinfo ) )
    return { "newstrickgraph": strickgraph.strickgraph_container( tmpstrickgraph ) }
relax_pressure: factory_leaf = factory_leaf( _rp_create_datagraphs, _rp_call_function, \
                            name = __name__ + ".improvestrickgraph pressure")
"""relax pressure via removein stitches.

.. autofunction:: _rp_call_function
.. autofunction:: _rp_create_datagraphs
"""

def get_longest_series( tobeshortenedrows: list[int] ):
    assert len(set(tobeshortenedrows)) == len(tobeshortenedrows), \
                                                "doubles in intlist"
    tobeshortenedrows = sorted( tobeshortenedrows )
    currentrow = [ tobeshortenedrows[0] ]
    longestrow = tuple()
    for i in tobeshortenedrows[1:]:
        if abs( i - currentrow[-1] ) == 1:
            currentrow.append( i )
        else:
            if len( currentrow ) > len( longestrow ):
                longestrow = tuple( currentrow )
            currentrow = [ i ]
    if len(longestrow) == 0:
        longestrow = tuple( currentrow )
    return longestrow
