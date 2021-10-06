import networkx as _netx
#from . import strickgraph_weisfeiler_lehman_graph_hash as myhash
from extrasfornetworkx import weisfeiler_lehman_graph_hash
from .constants import machine_terms, handknitting_terms, WrongTermError
import itertools
from collections import Counter
from typing import Dict, Hashable, Iterable
from . import strickgraph_fromgrid as fromgrid 
from . import strickgraph_toknitmanual as toknitmanual
import numpy as np

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
        return _netx.get_node_attributes( self, "alternative_stitchtype" )

    def copy_with_alternative_stitchtype( self ):
        """Returns another strickgraph with replaced stitchtypes with 
        alternative stitchtypes

        :return: Returns strickgraph with same type as this object. Copy has \
                alternative stitchtype
        :rtype: type( self )
        """
        selfcopy = self.copy()
        newstitchtypes = _netx.get_node_attributes( selfcopy, \
                                                    "alternative_stitchtype" )
        _netx.set_node_attributes( selfcopy, newstitchtypes, "stitchtype" )
        return selfcopy



class strick_datacontainer( _netx.MultiDiGraph ):
    """Groundclass for fabric. Support for node and edges equivalent to fabric.

    :todo: only concentrate on methods, which equal a graph representation
    :todo: methods to be outsourced: get_rows, get_borders, get_connected_nodes,
            get_nodes_near_nodes, get_startside, find_following_row, 
            give_next_node_to, get_sidemargins_indices, get_sidemargins
    :todo: isvalid should me a method which works not only for strickgraphs
    """
    def __init__( self, *args, **argv ):
        """Use .from_gridgraph, .from_manual"""
        super().__init__( *args, **argv )

    def _get_nodeattr( self, attrname ):
        subgraph = self.subgraph( set(self.nodes()) )
        return { a:b[attrname] for a,b in subgraph.nodes( data=True ) }
    def get_nodeattr_stitchtype( self ):
        return self._get_nodeattr( "stitchtype" )
    def get_nodeattr_side( self ):
        return self._get_nodeattr( "side" )
    def get_nodeattr_startingpoint( self ):
        return self._get_nodeattr( "startingpoint" )
    def get_nodeattr_alternativestitchtype( self ):
        return self._get_nodeattr( "alternativestitchtype" )

    def get_nodeattributes( self ):
        """Needed for verbesserer

        :todo: rework so that start and end have data
        """
        #subgraph = self.subgraph( set(self.nodes())-{"start", "end"})
        subgraph = self.subgraph( set(self.nodes()) )
        nodeplusdata = { a:b for a,b in subgraph.nodes( data=True ) }
        if "start" in nodeplusdata:
            nodeplusdata["start"] = {"stitchtype": "start", "side":"" }
        if "end" in nodeplusdata:
            nodeplusdata["end"] = {"stitchtype": "end", "side":"" }
        return { node:(data["stitchtype"], data["side"]) \
                        for node, data in nodeplusdata.items() }

    def get_nodes( self ):
        return self.nodes()

    def get_nodeattributelabel( self ):
        """

        :todo: remove this Method
        """
        nodedata = self.get_nodeattributes()
        nodestitchtype = { a:b[0] for a,b in nodedata.items() }
        nodeside = { a:b[1] for a,b in nodedata.items() }
        #nodestitchtype = _netx.get_node_attributes( self, "stitchtype" )
        #nodeside = _netx.get_node_attributes( self, "side" )
        #if 'start' in self.nodes():
        #    nodeside["start"] = ""
        #    nodestitchtype["start"] = "start"
        #if 'end' in self.nodes():
        #    nodeside["end"] = ""
        #    nodestitchtype["end"] = "end"
        nodelabels = { node: "".join(( nodestitchtype[node], nodeside[node])) \
                        for node in nodeside.keys() }
        #                if node not in ("start", "end" )}
        return nodelabels

    def get_edges_with_labels( self ):
        """Needed for verbesserer"""
        #subgraph = self.subgraph( set(self.nodes())-{"start", "end"})
        subgraph = self.subgraph( set(self.nodes()) )
        return tuple( (e[0], e[1], e[-1]["edgetype"]) \
                        for e in subgraph.edges( data=True ) )

    def get_startstitch( self ):
        nodes = set( self.get_nodes() )
        nodes.difference_update( v2 \
                        for v1, v2, edgetype in self.get_edges_with_labels() \
                        if edgetype=="next" )
        assert len( nodes ) == 1, f"multiple nodes with single "\
                                    f"outedge found {nodes}"
        return iter(nodes).__next__()

    def get_endstitch( self ):
        nodes = set( self.get_nodes() )
        nodes.difference_update( v1 \
                        for v1, v2, edgetype in self.get_edges_with_labels() \
                        if edgetype=="next" )
        assert len( nodes ) == 1, f"multiple nodes with single "\
                                    f"inedge found {nodes}"
        return iter(nodes).__next__()



    def get_rows( self, presentation_type="machine" ):
        rows = []
        #firststitch = self.give_next_node_to( "start" )
        firststitch = self.give_next_node_to( self.get_startstitch() )
        endstitch = self.get_endstitch()
        while firststitch != endstitch:
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
        """gives the borders as lists

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
    

    def get_connected_nodes( self, nodelist ):
        """Return nodetuples of real nodes, which are connected
        
        :param nodelist: List of nodes of this graph to check
        :type nodelist: Hashable
        :rtype: Iterable
        """
        asd = self.give_real_graph()
        helpgraph = _netx.Graph()
        helpgraph.add_nodes_from( asd.nodes() )
        helpgraph.add_edges_from( asd.edges() )
        helpsubgraph = helpgraph.subgraph( nodelist )
        return list(_netx.connected_components( helpsubgraph ))

    def get_nodes_near_nodes( self, nodelist, maxdistance=3 ):
        """Find nodes near nodelist within given distance

        :param maxdistance: maximum distance to nodelist
        :type maxdistance: int
        :type nodelist: Iterable[ Hashable ]
        :rtype nodelist: Tuple[ Hashable ]
        """
        #asd = self.give_real_graph()
        helpgraph = _netx.Graph()
        helpgraph.add_nodes_from( self.nodes() )
        helpgraph.add_edges_from( self.edges() )
        nearthings = set( nodelist )
        for a,b in _netx.all_pairs_dijkstra_path( helpgraph,cutoff=maxdistance):
            if a in nodelist:
                nearthings.update( b.keys() )
        return tuple( nearthings )

    def get_startside( self ):
        """Get startside"""
        firststitch = self.give_next_node_to( "start" )
        firstrow = self.find_following_row( firststitch )
        nodeattr = _netx.get_node_attributes( self, "side" )
        return nodeattr[ firstrow[0] ]

    def find_following_row( self, firstnode ):
        """return the row of this node, the start of the row will be the 
        node itself.

        :todo: i dont like breaks
        """
        node_side = _netx.get_node_attributes( self, "side" )
        rowside = node_side[ firstnode ]

        row = []
        tmpnode = firstnode
        while rowside == node_side.get( tmpnode, "" ) and tmpnode != "end":
            row.append( tmpnode )
            tmpnode = self.give_next_node_to( tmpnode )
        return row

    def give_next_node_to( self, node ):
        edges = self.edges( node, data=True )
        nextedges = [ x for x in edges if x[2]["edgetype"] == "next" ]
        try:
            return nextedges[0][1]
        except IndexError as err:
            raise Exception( edges, node )

    def get_sidemargins_indices( self, marginsize=5 ):
        rows = self.get_rows( "machine" )
        fetchsize = marginsize - 1
        leftindices = [marginsize]*len(rows)
        rightindices = [ -marginsize for row in rows ]
        for i in range( 0, len(rows) ):
            leftside = rows[i][ :marginsize ] 
            rightside = rows[i][ -marginsize: ]
            leftneighs = self.get_nodes_near_nodes( leftside, maxdistance=1 )
            rightneighs = self.get_nodes_near_nodes( rightside, maxdistance=1 )
            loweri, upperi = i-1, i+1
            if loweri >= 0:
                index_leftdown = max( rows[ loweri ].index( node ) \
                                            for node in leftneighs \
                                            if node in rows[ loweri ] )
                index_rightdown = min( rows[ loweri ].index(node)-len(rows[ loweri ]) \
                                            for node in rightneighs \
                                            if node in rows[ loweri ] )
                leftindices[ loweri ] = max( leftindices[ loweri ], \
                                            index_leftdown )
                rightindices[ loweri ] = min( rightindices[ loweri ], \
                                            index_rightdown )
            if upperi < len(rows):
                index_leftup = max( rows[ upperi ].index( node ) \
                                            for node in leftneighs \
                                            if node in rows[ upperi ] )
                index_rightup = min( rows[ upperi ].index(node) -len(rows[ upperi ])\
                                            for node in rightneighs \
                                            if node in rows[ upperi ] )
                leftindices[ upperi ] = max( leftindices[ upperi ], \
                                            index_leftup )
                rightindices[ upperi ] = min( rightindices[ upperi ], \
                                            index_rightup )
        return leftindices, rightindices

    def get_sidemargins( self, marginsize=5 ):
        """Return nodes on left and right side"""
        leftindices, rightindices = self.get_sidemargins_indices( marginsize )
        rows = self.get_rows( "machine" )
        leftside = [ row[ :i ] for row, i in zip( rows, leftindices ) ]
        rightside = [ row[ i: ] for row, i in zip( rows, rightindices ) ]
        return leftside, rightside

    def isvalid( self ):
        nextoutedges = [a for a,b,i,data in self.edges( data=True, keys=True )\
                        if data["edgetype"]=="next" ]
        nextinedges = [b for a,b,i,data in self.edges( data=True, keys=True )\
                        if data["edgetype"]=="next" ]
        import collections as col
        a = col.Counter( nextoutedges )
        b = col.Counter( nextinedges )
        cond1 = len(set(self.nodes()).difference(set(a.keys()))) == 1
        cond2 = len(set(self.nodes()).difference(set(b.keys()))) == 1
        cond3 = set() == set(a.keys()).difference(self.nodes())
        cond4 = set() == set(b.keys()).difference(self.nodes())
        cond5 = set((1,)) == set(a.values())
        cond6 = set((1,)) == set(b.values())
        if not all((cond1, cond2, cond3, cond4, cond5, cond6)):
            messages = []
            messages.append( "nodes without outedges %s" \
                    %( set(self.nodes()).difference((*(a.keys()),)) ))
            messages.append( "nodes without inedges %s" \
                    %( set(self.nodes()).difference((*(b.keys()),)) ))
            q3 = set(a.keys()).difference(self.nodes())
            q4 = set(b.keys()).difference(self.nodes())
            q5 = [node for node, count in a.items() if count!=1 ]
            qq5 = [ [(a,b) for a,b,i,data in self.edges( data=True, keys=True )\
                        if data["edgetype"]=="next" and a==node] for node in q5]
            q6 = [node for node, count in b.items() if count!=1 ]
            qq6 = [ [(a,b) for a,b,i,data in self.edges( data=True, keys=True )\
                        if data["edgetype"]=="next" and b==node] for node in q6]
            raise Exception( *messages, q3, q4, qq5, qq6 )
        return all((cond1, cond2, cond3, cond4))



class strickgraph( strick_datacontainer, fromgrid.strick_fromgrid, \
                        strick_compare, alternative_stitchtype_support, \
                        strick_physic_forceproperties, \
                        toknitmanual.strick_manualhelper ):
    """QWERQWER

    asdf
    this is something
    """
    def __init__( self, *args, **argv ):
        """
        myinit
        """
        strick_datacontainer.__init__( self, *args, **argv )
        self.supergraph = self

    def give_real_graph( self ):
        return self.subgraph( set(self.nodes()).difference(["start", "end"]))

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
        if presentation_type in machine_terms:
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

