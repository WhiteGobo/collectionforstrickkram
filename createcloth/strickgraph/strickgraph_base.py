import networkx as _netx
#from . import strickgraph_weisfeiler_lehman_graph_hash as myhash
from extrasfornetworkx import weisfeiler_lehman_graph_hash_multidigraph
from .constants import machine_terms, handknitting_terms, WrongTermError
import itertools
from collections import Counter

from .strickgraph_helper import separate_to_rows

class strickgraph( _netx.MultiDiGraph ):
    def __init__( self, *args, **argv ):
        self.supergraph = self
        super().__init__( *args, **argv )

    def give_real_graph( self ):
        return self.subgraph( set(self.nodes()).difference(["start", "end"]))

    def subgraph( self, *args, **argv ):
        tmpsubgraph = super().subgraph( *args, **argv )
        tmpsubgraph.supergraph = self
        return tmpsubgraph

    def create_hashvalues( self ):
        a = _netx.get_node_attributes( self, "stitchtype" )
        b = _netx.get_node_attributes( self, "side" )
        hashattributes = { key: a[key]+b[key] for key in a }
        _netx.set_node_attributes( self, hashattributes, "hashval" )


    def __hash__( self ):
        self.supergraph.create_hashvalues()

        subgraph = self.subgraph( set(self.nodes())-{"start", "end"})
        #returnv  = int( myhash.weisfeiler_lehman_graph_hash( subgraph ),
        #                                            base = 16 )
        #return returnv
        returnv = weisfeiler_lehman_graph_hash_multidigraph( subgraph, \
                            #node_attr_list=["stitchtype", "side"], \
                            node_attr="hashval", \
                            edge_attr="edgetype",\
                            )
        return int( returnv, base=16 )

    def presort( self ):
        """
        magic method to know with which other graphs it wont definitly is 
        unequal
        :returns: hashable
        """
        self.supergraph.create_hashvalues()
        selfnodecount = Counter([ value for value \
                    in _netx.get_node_attributes( self, "hashval" ).values() ])
        trans = { str(e):e for e in selfnodecount.keys()}
        tmptuple = tuple( sorted( trans.keys() ))
        second = tuple( selfnodecount[trans[stre]] for stre in tmptuple )
        return (tmptuple, second)

    def __eq__( self, other ):
        try:
            self.supergraph.create_hashvalues()
            selfnodecount = Counter([ value for value \
                    in _netx.get_node_attributes( self, "hashval" ).values() ])

            other.supergraph.create_hashvalues()
            othernodecount = Counter([ value for value \
                    in _netx.get_node_attributes( other, "hashval" ).values() ])
            if selfnodecount != othernodecount:
                return False
        except Exception as err:
            return False

        return self.__hash__() == other.__hash__()

    def get_rows( self, presentation_type="machine" ):
        rows = []
        firststitch = self.give_next_node_to( "start" )
        while firststitch != "end":
            currentrow = self.find_following_row( firststitch )
            rows.append( currentrow )
            firststitch = self.give_next_node_to( currentrow[-1] )
        if presentation_type in machine_terms:
            #tmprows = [] #dont need this
            node_side = _netx.get_node_attributes( self, "side" )
            for row in rows:
                if node_side[ row[0] ] == "right":
                    pass
                else:
                    row.reverse()
                #tmprows.append( row )
            #rows = tmprows
        elif presentation_type in handknitting_terms:
            pass
        else:
            raise WrongTermError("get_rows can only print in handknitting or"
                            +" machine terms. see pkg/strickgraph/constants.py")
        return rows
        #firstrow = self.find_following_row( firststitch )
        #subgraph = self.subgraph( set(self.nodes())-{"start", "end"})
        #rows = separate_to_rows( subgraph, firstrow )
        #return rows

    def get_borders( self ):
        """
        gives the borders as lists
        :todo: from a single row multiple stitches can contribute to each border
        :rtype down, up, left, right: list, list, list, list
        :return: down, up, left, right
        """
        rows = self.get_rows( presentation_type="machine" )

        down = rows[0]
        up = rows[-1]
        left = [ tmprow[0] for tmprow in rows ] #todo: instead march through
        right = [ tmprow[-1] for tmprow in rows ] #todo: instead march through
        return down, up, left, right

    def get_startside( self ):
        firststitch = self.give_next_node_to( "start" )
        firstrow = self.find_following_row( firststitch )
        nodeattr = _netx.get_node_attributes( self, "side" )
        return nodeattr[ firstrow[0] ]

    def find_following_row( self, firstnode ):
        """
        return the row of this node, the start of the row will be the node
        itself
        :todo: i dont like breaks
        """
        node_side = _netx.get_node_attributes( self, "side" )
        rowside = node_side[ firstnode ]

        row = []
        tmpnode = firstnode
        while rowside == node_side[ tmpnode ]:
            row.append( tmpnode )
            tmpnode = self.give_next_node_to( tmpnode )
            if tmpnode == "end":
                break

        return row


    def give_next_node_to( self, node ):
        edges = self.edges( node, data=True )
        nextedges = [ x for x in edges if x[2]["edgetype"] == "next" ]
        return nextedges[0][1]


def get_neighbours_from( strickgraph, nodelist ):
    neighbours = set()
    for node in nodelist:
        neighbours.update( strickgraph.successors( node ) )
        neighbours.update( strickgraph.predecessors( node ) )
    neighbours = neighbours.difference( nodelist )
    return neighbours

class stricksubgraph( strickgraph ):
    """
    this class is extra for strickgraph patches
    """
    def get_rows( self, presentation_type="thread" ):
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

        asd =  sort_nodes_downtoup( left_nodes, right_nodes, next_edges, up_edges )
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
        if presentation_type in machine_terms:
            rows = reverse_every_second_row( rows, firstside= side_of_nodes[ rows[0][0] ] )

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

