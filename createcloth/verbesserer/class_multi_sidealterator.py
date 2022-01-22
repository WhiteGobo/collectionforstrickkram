#from .verbesserer_class import FindError, strickalterator
from ..plainknit.class_identifier import create_graph_from_linetypes
from .class_side_alterator import NoTranslationPossible
from . import class_side_alterator as _csa
import xml.etree.ElementTree as ET
import logging
import extrasfornetworkx as efn
from extrasfornetworkx import class_verbesserer as cver
from extrasfornetworkx import xml_config
from extrasfornetworkx import class_multiverbesserer as cmultiver
import networkx as netx
import itertools as it
import math
from .. import helper_limitcalculationtime as timelimiter
from ..strickgraph import strickgraph
logger = logging.getLogger( __name__ )
from ..stitchinfo import basic_stitchdata as glstinfo
from dataclasses import dataclass
from typing import Iterable
import time

class multi_sidealterator( efn.multialterator ):
    """Multi alteratorclass for sidealterator
    
    :todo: overhaul this method, when removing unused things in this directory
    :ivar alteratorlist: inherited from sidealterator
    :ivar exclusion_criteria: inherited from sidealterator
            
    """
    def __init__( self, side_alterator_list, **kwargs ):
        """

        :param kwargs: will passed down to parent.__init__
        """
        #for alt in side_alterator_list:
        #    assert type( alt ) == asdf
        super().__init__( side_alterator_list, **kwargs )
        self.side_alterator_list = side_alterator_list

    @dataclass
    class linetypepair:
        """helperclass for generate_from_linetypelist input.
        will only be used as iterable so instead iterable conforming to
        __iter__ can be used instead
        """
        input_linetypelist: Iterable
        output_linetypelist: Iterable
        input_upedges: Iterable[ int ]
        output_upedges: Iterable[ int ]
        changed_line: int
        startside: str
        def __iter__( self ):
            """
            :rtype: Iterable, Iterable, Iterable[ int ], Iterable[ int ], int, str
            """
            yield self.input_linetypelist
            yield self.output_linetypelist
            yield self.input_upedges
            yield self.output_upedges
            yield self.changed_line
            yield self.startside

    @classmethod
    def generate_from_linetypelist( cls, linetypepairlists, \
                                    starting_side_alterator_list=[], \
                                    maximum_uncommon_nodes=30, timelimit=None,\
                                    soft_timelimit=None, \
                                    soft_maximum_uncommon_nodes=None,
                                    **kwargs ):
        """Method for automativ creation of side_alterator

        :param linetypepairlists: Input for sidealterator.from_replacement
        :type linetypepairlists: Iterable[ cls.linetypepair ]
        :todo: here is a short debug for not working extrafornetworkx optimize
        """
        def use_alterator( tmpalterator, linetype_in, linetype_out, \
                                upedges_in, upedges_out, changedline_id, \
                                startside, **kwargs_alterate):
            #logger.debug( "test alterator for %s" %(
            #        cls.linetypepair( linetype_in, linetype_out, upedges_in, \
            #                upedges_out, changedline_id, startside ) ))
            tmp_graph = create_graph_from_linetypes( linetype_in, upedges_in, \
                                        startside=startside, **kwargs_alterate )
            try:
                repl_graph = tmpalterator.replace_graph( tmp_graph, \
                                        changedline_id )
            except (cver.ExcludeAssertion, cver.NoTranslationPossible, cver.MultipleTranslationFound): #just to show exceptions are expected
                raise
            great_graph = create_graph_from_linetypes( linetype_out, upedges_out,\
                                        startside=startside, **kwargs_alterate )
            #return repl_graph == great_graph
            if repl_graph == great_graph:
                return True
            else:
                logger.debug( 
                        ("found wrong replacement, as existing alterator: "\
                        "input: %s, output: %s, expected: %s, "\
                        "notes in used alterator: %s" ) \
                        %( tmp_graph.to_manual( glstinfo ).replace("\n",";"), \
                        repl_graph.to_manual( glstinfo ).replace("\n",";"), \
                        great_graph.to_manual( glstinfo ).replace("\n",";"), \
                        tmpalterator.notes )
                        )
                return False
        def create_alterator( linetype_in, linetype_out, upedges_in, \
                                upedges_out, changedline_id, startside, \
                                **kwargs_create ):
            logger.info( "in: %s" %( str(linetype_in) ) )
            logger.info( "out: %s" %( str(linetype_out) ) )
            logger.info( str((upedges_in, upedges_out, changedline_id)) )
            notes = "generatedfrom:in: %s, out: %s"\
                    %( str(linetype_in), str(linetype_out) )
            if timelimit is not None:
                kwargs_create[ "timelimit" ] = timelimit
            try:
                return _csa.sidealterator.from_linetypes( \
                                linetype_out, linetype_in, \
                                upedges_out, upedges_in, changedline_id, \
                                maximum_uncommon_nodes = maximum_uncommon_nodes, \
                                startside=startside, **gen_extraoptions, \
                                **kwargs_create )
            except Exception as err:
                raise cmultiver.SkipAlteration() from err

        #q = it.chain.from_iterable( ((linepair_info, { "startside":"left"}), \
        #                        (linepair_info, { "startside":"right"})) \
        #                        for linepair_info in linetypepairlists )
        gen_extraoptions = {}
        if soft_timelimit is not None and soft_maximum_uncommon_nodes is not None:
            gen_extraoptions["soft_timelimit"] = soft_timelimit
            gen_extraoptions["soft_maximum_uncommon_nodes"] = soft_maximum_uncommon_nodes
        q = zip( linetypepairlists, [{}]*len( linetypepairlists ) )
        return cls.from_replacements( q,
                    replace_function = use_alterator, \
                    alterator_generator = create_alterator, \
                    starting_generatorlist = starting_side_alterator_list, \
                    **kwargs )


    def replace_graph( self, graph, changeline ):
        """Replace in given Strickgraph at given line. Gives back new
        strickgraph with replaced parts. Raises 'NoTranslationPossible'
        if replacement is not possible

        :raises: NoTranslationPossible
        :returns: Strickgraph with replaced parts
        :rtype: strickgraph
        """
        row = graph.get_rows()[ changeline ]
        nodeattributes = graph.get_nodeattributes()
        edgeswithlabel = graph.get_edges_with_labels()
        try:
            return super().replace_graph( graph, changeline, row=row, \
                                nodeattributes=nodeattributes )
        except cver.NoTranslationPossible as err:
            raise NoTranslationPossible() from err

    @classmethod
    def fromxml( cls, xmlstring ):
        self = super().fromxml( xmlstring, alteratortype=_csa.sidealterator )
        return self
