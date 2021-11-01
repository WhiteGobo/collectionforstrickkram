import networkx as _netx
#from . import strickgraph_weisfeiler_lehman_graph_hash as myhash
from extrasfornetworkx import weisfeiler_lehman_graph_hash
import itertools
from collections import Counter
from typing import Dict, Hashable, Iterable
from .. import strickgraph as mod_strickgraph
from . import strickgraph_fromgrid as fromgrid 
from . import strickgraph_toknitmanual as toknitmanual
import numpy as np
from .datacontainer import strick_datacontainer

#from .strickgraph_helper import separate_to_rows


class strick_physic_forceproperties:
    def set_positions( self, positions: Dict[ Hashable, Dict ] ):
        realgraph = self.give_real_graph()
        if set( positions.keys() ) != set( realgraph.nodes() ):
            raise Exception( "set position needs dictionary with every node" )
        _netx.set_node_attributes( self, positions )
        elengths = dict()
        posarrays = { node: tuple( q[c] for c in ("x", "y", "z")) \
                            for node, q in positions.items() }
        length_dictionary = {}
        for e in realgraph.edges( keys=True ):
            l = np.linalg.norm( np.subtract(posarrays[e[0]], posarrays[e[1]] ))
            length_dictionary[e] = l
        _netx.set_edge_attributes( self, length_dictionary, "currentlength" )


    def set_calmlength( self, mythreadinfo ):
        """
        :param mythreadinfo: createcloth.physicalhelper.threadinfo
        """
        downstitchlength = mythreadinfo.plainknit_startstitchwidth
        upstitchlength = mythreadinfo.plainknit_endstitchwidth
        sidestitchlength = mythreadinfo.plainknit_stitchheight
        lengthdict = {}
        #realdings = self.get_real_graph
        for e in self.edges( keys=True ):
            lengthdict[ e ] = upstitchlength
        _netx.set_edge_attributes( self, lengthdict, "length" )


class strick_compare:
    def __hash__( self ):
        nodelabels = self.get_nodeattributelabel()
        edges = self.get_edges_with_labels()
        return weisfeiler_lehman_graph_hash( nodelabels, edges )

    def __eq__( self, other ):
        if type(self)!=type(other):
            return False
        return self.__hash__() == other.__hash__()


class alternative_stitchtype_support():
    """

    :todo: Implement alternative stitchtype via this __init__
    """
    #def __init__( self ):
    def get_alternative_stitchtypes( self ):
        """Return alternative stitchtypes to stitches. Only returns nodes with
        alternative stitchtype

        :return: Return dictionary with node to stitchtype
        :rtype: Dict[ Hashable, str ]
        """
        raise Exception()
        return _netx.get_node_attributes( self, "alternative_stitchtype" )

    def copy_with_alternative_stitchtype( self ):
        """Returns another strickgraph with replaced stitchtypes with 
        alternative stitchtypes

        :return: Returns strickgraph with same type as this object. Copy has \
                alternative stitchtype
        :rtype: type( self )
        """
        mytrans = lambda data: {"stitchtype":data[0], "side":data[1]}
        nodeattr = { a: mytrans(data) for a, data in self.get_nodeattributes().items() }
        for n, alt in self._get_nodeattr( "alternative_stitchtype" ).items():
            nodeattr[n]["stitchtype"] = alt
        edges = self.get_edges_with_labels()
        return type(self)( nodeattr, edges )





class strickgraph( fromgrid.strick_fromgrid, \
                        strick_compare, alternative_stitchtype_support, \
                        strick_physic_forceproperties, \
                        toknitmanual.strick_manualhelper ):
    """QWERQWER

    asdf
    this is something
    """
    def __init__( self, nodeattributes, edgelabels, **argv ):
        """
        myinit
        """
        strick_datacontainer.__init__( self, nodeattributes, edgelabels )
        self.supergraph = self

    def subgraph( self, *args, **argv ):
        tmpsubgraph = super().subgraph( *args, **argv )
        tmpsubgraph.supergraph = self
        return tmpsubgraph

    #def __hash__( self ):
    #    return strick_compare.__hash__( self )


def get_neighbours_from( strickgraph, nodelist ):
    neighbours = set()
    for node in nodelist:
        neighbours.update( strickgraph.successors( node ) )
        neighbours.update( strickgraph.predecessors( node ) )
    neighbours = neighbours.difference( nodelist )
    return neighbours

class stricksubgraph( strickgraph ):
    """this class is extra for strickgraph patches"""
    def get_rows( self, presentation_type="thread" ):
        """Get list of graphnode-rows.
        You can get a threadlike construct, which shows first the first one you
        would knit.
        You can get a machinelike construct where you get a form which 
        corresponds to as-seen, when knitted.

        :param presentation_type: 'machine' or 'thread
        :rtype: List[ List[ Hashable ]]
        """
        raise Exception()
        side_of_nodes = _netx.get_node_attributes( self, "side" )
        all_edges = self.edges( data=True, keys=True )
        up_edges = [ (edge[0],edge[1]) for edge in all_edges \
                        if edge[3]["edgetype"]=="up"]
        next_edges = [ (edge[0], edge[1]) for edge in all_edges \
                        if edge[3]["edgetype"]=="next"]
        left_nodes = [ node for node in self.nodes \
                        if side_of_nodes[ node ] == "left" ]
        right_nodes = [ node for node in self.nodes \
                        if side_of_nodes[ node ] == "right" ]

        asd =  sort_nodes_downtoup( left_nodes, right_nodes, \
                                    next_edges, up_edges )
        rows = []
        currentrow = []
        rows.append( currentrow )
        if asd[0] in left_nodes:
            left=True
        else:
            left=False
        for node in asd:
            if left != (node in left_nodes): #switched side
                currentrow = []
                rows.append( currentrow )
                left = (node in left_nodes)
            currentrow.append( node )
        if presentation_type in mod_strickgraph.machine_terms:
            rows = reverse_every_second_row( rows, \
                                    firstside= side_of_nodes[ rows[0][0] ] )

        return rows

def reverse_every_second_row( rows, firstside="right" ):
    rev_i = {"right":0, "left":1}[ firstside ] #0 if right; 1 if left
    for i in range( len( rows )):
        if i%2 == rev_i:
            tmprow = rows[i]
            tmprow.reverse()
    return rows
            

def sort_nodes_via_edges( nodes, edges ):
    sortgraph = _netx.DiGraph()
    sortgraph.add_nodes_from( nodes )
    for node1, node2 in edges:
        if node1 in nodes and node2 in nodes:
            sortgraph.add_edge( node1, node2 )
    ordered_nodes = _netx.algorithms.dag.topological_sort( sortgraph )
    return list( ordered_nodes )


def sort_nodes_downtoup( left_nodes, right_nodes, next_edges, up_edges ):
    next_edges = [ edge for edge in next_edges \
                    if (edge[0] in left_nodes and edge[1] in left_nodes) \
                    or (edge[0] in right_nodes and edge[1] in right_nodes) ]
    nodes = set( left_nodes ).union( right_nodes )
    groupgraph = _netx.Graph()
    groupgraph.add_nodes_from( nodes )
    groupgraph.add_edges_from( next_edges )
    horizontal_groups = \
            list( _netx.algorithms.components.connected_components( \
                                groupgraph ) )


    horizontal_groups = [ sort_nodes_via_edges( nodes, next_edges ) \
                            for nodes in horizontal_groups ]

    nodetogroup_dict = {}
    for i in range( len(horizontal_groups) ):
        for node in horizontal_groups[i]:
            nodetogroup_dict.update({ node:i })

    new_up_edges = []
    for edge in up_edges:
        newnode1 = nodetogroup_dict[ edge[0] ]
        newnode2 = nodetogroup_dict[ edge[1] ]
        new_up_edges.append( (newnode1, newnode2) )

    vert_groupgraph = _netx.DiGraph()
    vert_groupgraph.add_nodes_from( range(len(horizontal_groups)) )
    vert_groupgraph.add_edges_from( new_up_edges )
    asd = _netx.algorithms.dag.topological_sort( vert_groupgraph )

    asd = [ list(horizontal_groups[i]) for i in asd ]
    return list( itertools.chain( *asd ) )

