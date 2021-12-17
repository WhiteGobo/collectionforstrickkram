import networkx as _netx
from .. import strickgraph as mod_strickgraph
import itertools as it

maximaldataset_per_node = set(("stitchtype", "side", "alternativestitchtypes"))
minimaldataset_per_node = set(("stitchtype", "side"))

class strick_datacontainer():
    """Groundclass for fabric. Support for node and edges equivalent to fabric.

    :todo: only concentrate on methods, which equal a graph representation
    :todo: methods to be outsourced: get_rows, get_borders, get_connected_nodes,
            get_nodes_near_nodes, get_startside, find_following_row, 
            give_next_node_to, get_sidemargins_indices, get_sidemargins
    :todo: isvalid should me a method which works not only for strickgraphs
    """
    def __init__( self, nodeattributes, edgelabels ):
        """

        :type nodeattributes: Dict[ Hashable, Dict ]
        :type edgelabels: Iterable[ Tuple[ Hashable, Hashable, str ]]
        """
        self.__datacontainer = _netx.MultiDiGraph()
        for node, data in nodeattributes.items():
            assert data["side"] in ("left", "right"), f"side is strange: {node} {data}"
            self.__datacontainer.add_node( node, **data )
            assert minimaldataset_per_node.issubset( data.keys() ), data
            assert maximaldataset_per_node.issuperset( data.keys() ), data
        for v1, v2, label in edgelabels:
            self.__datacontainer.add_edge( v1, v2, edgetype=label )
    #def __init__( self, *args, **argv ):
    #    """Use .from_gridgraph, .from_manual"""
    #    super().__init__( *args, **argv )

    def _get_nodeattr( self, attrname ):
        graph = self.__datacontainer
        return { a:b[attrname] for a,b in graph.nodes( data=True ) \
                if attrname in b }
    def get_nodeattr_stitchtype( self ):
        """

        :rtype: Dict[ Hashable, str ]
        """
        return self._get_nodeattr( "stitchtype" )
    def get_nodeattr_side( self ):
        """

        :rtype: Dict[ Hashable, str ]
        """
        return self._get_nodeattr( "side" )
    def get_nodeattr_alternativestitchtype( self ):
        """

        :rtype: Dict[ Hashable, str ]
        :todo: maybe remove alternativestitchtype
        """
        return self._get_nodeattr( "alternativestitchtype" )

    def subgraph( self, nodes ):
        mytrans = lambda data: {"stitchtype":data[0], "side":data[1]}
        nodeattr = { a: mytrans(data) for a, data in self.get_nodeattributes().items() }
        edges = self.get_edges_with_labels()
        sub_nodeattr = { n:attr for n, attr in nodeattr.items() if n in nodes }
        sub_edges = list( (v1, v2, label) for v1, v2, label in edges \
                        if v1 in nodes and v2 in nodes )
        return type(self)( sub_nodeattr, sub_edges )

    def get_nodeattributes( self ):
        """Needed for verbesserer

        :todo: rework so that start and end have data
        :rtype: Dict[ Hashable, Tuple ]
        """
        #subgraph = self.subgraph( set(self.nodes())-{"start", "end"})
        #subgraph = self.subgraph( set(self.nodes()) )
        nodeplusdata = { a:b for a,b in self.__datacontainer.nodes( data=True ) }
        if "start" in nodeplusdata:
            nodeplusdata["start"] = {"stitchtype": "start", "side":"" }
        if "end" in nodeplusdata:
            nodeplusdata["end"] = {"stitchtype": "end", "side":"" }
        return { node:(data["stitchtype"], data["side"]) \
                        for node, data in nodeplusdata.items() }

    def get_nodes( self ):
        """

        :rtype: Iterable[ Hashable ]
        :todo: move this to get_stitches
        """
        return self.__datacontainer.nodes()

    def get_nodeattributelabel( self ):
        """

        :todo: remove this Method
        """
        nodedata = self.get_nodeattributes()
        nodestitchtype = { a:b[0] for a,b in nodedata.items() }
        nodeside = { a:b[1] for a,b in nodedata.items() }
        nodelabels = { node: "".join(( nodestitchtype[node], nodeside[node])) \
                        for node in nodeside.keys() }
        return nodelabels

    def get_edges_with_labels( self ):
        """Needed for verbesserer
        
        :rtype: Iterable[ Tuple[ Hashable, Hashable, str ] ]
        """
        return tuple( (e[0], e[1], e[-1]["edgetype"]) \
                        for e in self.__datacontainer.edges( data=True ) )
        #subgraph = self.subgraph( set(self.nodes())-{"start", "end"})
        subgraph = self.subgraph( set(self.get_nodes()) )
        return tuple( (e[0], e[1], e[-1]["edgetype"]) \
                        for e in subgraph.edges( data=True ) )

    def get_startstitch( self ):
        """

        :todo: This is no permanent method. I willchange strickgraph to
            include multiple threads.
        """
        raise Exception()
        nodes = set( self.get_nodes() )
        nodes.difference_update( v2 \
                        for v1, v2, edgetype in self.get_edges_with_labels() \
                        if edgetype=="next" )
        assert len( nodes ) == 1, f"multiple nodes with single "\
                                    f"outedge found {nodes}"
        return iter(nodes).__next__()

    def get_endstitch( self ):
        """

        :todo: This is no permanent method. I willchange strickgraph to
            include multiple threads.
        """
        nodes = set( self.get_nodes() )
        nodes.difference_update( v1 \
                        for v1, v2, edgetype in self.get_edges_with_labels() \
                        if edgetype=="next" )
        assert len( nodes ) == 1, f"multiple nodes with single "\
                                    f"inedge found {nodes}"
        return iter(nodes).__next__()

    
    def _get_topologicalsort_of_stitches( self ):
        sorted_stitches = list( _netx.topological_sort( self.__datacontainer ))
        return sorted_stitches


    def get_rows( self, presentation_type="machine" ):
        """

        :todo: move this a classlayer up
        """
        stitchside = self.get_nodeattr_side()
        sorted_stitches = self._get_topologicalsort_of_stitches()
        currentrow = [ sorted_stitches[0] ]
        rows = [ currentrow ]
        laststitch = sorted_stitches[0]
        lastside = stitchside[ laststitch ]
        for stitch in sorted_stitches[1:]:
            nextside = stitchside[ stitch ]
            if lastside == nextside:
                currentrow.append( stitch )
            else:
                lastside = nextside
                currentrow = [ stitch ]
                rows.append( currentrow )
        
        #rows = []
        #firststitch = self.get_startstitch()
        #endstitch = self.get_endstitch()
        #while firststitch != endstitch:
        #    currentrow = self.find_following_row( firststitch )
        #    rows.append( currentrow )
        #    if currentrow[ -1 ] == endstitch:
        #        break
        #    firststitch = self.give_next_node_to( currentrow[-1] )
        if presentation_type in mod_strickgraph.machine_terms:
            node_side = self.get_nodeattr_side()
            for row in rows:
                if node_side[ row[0] ] == "right":
                    pass
                else:
                    row.reverse()
        elif presentation_type in mod_strickgraph.handknitting_terms:
            pass
        else:
            raise mod_strickgraph.WrongTermError("get_rows can only print "\
                            +"in handknitting or" \
                            +" machine terms. see pkg/strickgraph/constants.py")
        return rows

    def get_neighbours_to( self, stitchnode ):
        """Finds all neighbours to node.

        :param stitchnode: Node in the strickgraph
        :returns: Nodelist of all neighbours
        :rtype: List[ Hashable ]
        """
        edges = self.get_edges_with_labels()
        filteredges = ( (v1, v2) for v1, v2, etype in edges \
                        if stitchnode in (v1, v2) )
        nodes = set( it.chain.from_iterable( filteredges ) )
        nodes.remove( stitchnode )
        return nodes

    def get_borders( self ):
        """gives the borders as lists

        :todo: Must be alterated if cuts from above or below are possible
        :todo: move one class layer up
        :rtype: Tuple[ List[Hashable],... ]
        :return: down, up, left, right
        """
        rows = self.get_rows( presentation_type="machine" )

        down = rows[0]
        up = rows[-1]
        left = []
        right = []
        for i, tmprow in enumerate(rows):
            #for easier algorithm max and min
            uprow = set( rows[ min( i+1, len(rows)-1 ) ] )
            downrow = set( rows[ max( i-1, 0 ) ] )
            j, neighs, left_tmp = -1, [], []
            while len(uprow.intersection( neighs ))==0 \
                            or len(downrow.intersection(neighs))==0:
                j += 1
                tmp = tmprow[j]
                left_tmp.append( tmp )
                neighs = self.get_neighbours_to( tmp )
            if len( downrow.intersection( self.get_neighbours_to( left_tmp[0] )))==0:
                left_tmp.reverse()
            left.extend( left_tmp )
            j, neighs, right_tmp = 0, [], []
            while len(uprow.intersection( neighs ))==0 \
                            or len(downrow.intersection(neighs))==0:
                j -= 1
                tmp = tmprow[j]
                right_tmp.append( tmp )
                neighs = self.get_neighbours_to( tmp )
            if len( uprow.intersection( self.get_neighbours_to( right_tmp[0] )))==0:
                right_tmp.reverse()
            right.extend( right_tmp )
        return down, up, left, right
    

    def get_connected_nodes( self, nodelist ):
        """Return nodetuples of real nodes, which are connected
        
        :param nodelist: List of nodes of this graph to check
        :type nodelist: Hashable
        :rtype: Iterable
        """
        #asd = self.give_real_graph()
        helpgraph = _netx.Graph()
        helpgraph.add_nodes_from( self.get_nodes() )
        helpgraph.add_edges_from( [e[:2] for e in self.get_edges_with_labels()] )
        helpsubgraph = helpgraph.subgraph( nodelist )
        return list(_netx.connected_components( helpsubgraph ))

    def get_nodes_near_nodes( self, nodelist, maxdistance=3 ):
        """Find nodes near nodelist within given distance

        :param maxdistance: maximum distance to nodelist
        :type maxdistance: int
        :type nodelist: Iterable[ Hashable ]
        :returns: nodes in distance < 'maxdistance'
        :rtype: Tuple[ Hashable,... ]
        """
        #asd = self.give_real_graph()
        helpgraph = _netx.Graph()
        helpgraph.add_nodes_from( self.get_nodes() )
        helpgraph.add_edges_from( [e[:2] for e in self.get_edges_with_labels()])
        nearthings = set( nodelist )
        for a,b in _netx.all_pairs_dijkstra_path( helpgraph,cutoff=maxdistance):
            if a in nodelist:
                nearthings.update( b.keys() )
        return tuple( nearthings )

    def get_startside( self ):
        """Get startside

        :rtype: str
        :todo: remove this method
        """
        #firststitch = self.give_next_node_to( "start" )
        nodeattr = _netx.get_node_attributes( self.__datacontainer, "side" )
        firstrow = self.get_rows()[0]
        return nodeattr[ firstrow[0] ]
        #firststitch = self.get_startstitch()
        #endstitch = self.get_endstitch()
        firstrow = self.find_following_row( firststitch )
        nodeattr = _netx.get_node_attributes( self.__datacontainer, "side" )
        return nodeattr[ firstrow[0] ]

    def find_following_row( self, firstnode ):
        """return the row of this node, the start of the row will be the 
        node itself.

        :todo: i dont like breaks
        """
        node_side = _netx.get_node_attributes( self.__datacontainer, "side" )
        rowside = node_side[ firstnode ]
        endstitch = self.get_endstitch()

        row = []
        tmpnode = firstnode
        while rowside == node_side.get( tmpnode, "" ):
            row.append( tmpnode )
            if tmpnode == endstitch:
                break
            else:
                tmpnode = self.give_next_node_to( tmpnode )
        return row

    def give_next_node_to( self, node ):
        """When following the thread, the next stitch.

        :rtype: Hashable
        :todo: Hash no failsafe for last stitch
        """
        edges = [ (a,b, label) for a,b,label in self.get_edges_with_labels()\
                        if a==node ]
        nextedges = [ x for x in edges if x[2] == "next" ]
        return nextedges[0][1]

    def get_sidemargins_indices( self, marginsize=5 ):
        """Returns the indices of the sidemargin. In every node a minimum
        of 'marginsize' stitches are indexed. Also there may be more, so
        that of every minimalsidemargin-stitch also the up and downneighbour
        is included. 
        E.g. if the first row has 7 stitches and second 5 there must be 2
        additional stitches from the first row, because they are neighbours
        to stitches in the second row.

        :rtype: Tuple[ Iterable[ int ], Iterable[ int ] ]
        :returns: Two lists of indices of sidemargins, so that up- and 
                downneighbours are also included.
        :todo: move one class layer up
        """
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
            assert leftneighs
            assert rightneighs
            if loweri >= 0:
                try:
                    index_leftdown = max( rows[ loweri ].index( node ) \
                                            for node in leftneighs \
                                            if node in rows[ loweri ] )
                    leftindices[ loweri ] = max( leftindices[ loweri ], \
                                            index_leftdown )
                except ValueError:
                    pass 
                    #catches if minimal border isnt far enough to be
                    #neighbouring to upper border
                try:
                    index_rightdown = min( rows[ loweri ].index(node) \
                                            - len(rows[ loweri ]) \
                                            for node in rightneighs \
                                            if node in rows[ loweri ] )
                    rightindices[ loweri ] = min( rightindices[ loweri ], \
                                            index_rightdown )
                except ValueError:
                    pass #see above
            if upperi < len(rows):
                try:
                    index_leftup = max( rows[ upperi ].index( node ) \
                                            for node in leftneighs \
                                            if node in rows[ upperi ] )
                    leftindices[ upperi ] = max( leftindices[ upperi ], \
                                            index_leftup )
                except ValueError:
                    pass #see above
                try:
                    index_rightup = min( rows[ upperi ].index(node) \
                                            - len(rows[ upperi ])\
                                            for node in rightneighs \
                                            if node in rows[ upperi ] )
                    rightindices[ upperi ] = min( rightindices[ upperi ], \
                                            index_rightup )
                except ValueError:
                    pass #see above
        return leftindices, rightindices

    def get_sidemargins( self, marginsize=5 ):
        """Returns stitches, with their respective identifier. Returned
        stitches correspond to the method :py:method:`get_sidemargins_indices`

        :rtype: Tuple[ Iterable[ Hashable ], Iterable[ Hashable ] ]
        :returns: right and left list of sidemargin-stitches
        :todo: move one class layer up
        """
        leftindices, rightindices = self.get_sidemargins_indices( marginsize )
        rows = self.get_rows( "machine" )
        leftside = [ row[ :i ] for row, i in zip( rows, leftindices ) ]
        rightside = [ row[ i: ] for row, i in zip( rows, rightindices ) ]
        return leftside, rightside

    def isvalid( self ):
        """Checks if ggraph corresponds to a valid strickgraph. Exists only
        for programchecking reasons.

        :rtype: Bool
        :todo: use logging instead of raising exception
        :todo: maybe remove this and instead make valid checks, when creating 
                strickgraphs
        """
        nextoutedges = [a for a,b,label in self.get_edges_with_labels()\
                        if label=="next" ]
        nextinedges = [b for a,b,label in self.get_edges_with_labels()\
                        if label=="next" ]
        import collections as col
        a = col.Counter( nextoutedges )
        b = col.Counter( nextinedges )
        cond1 = len(set(self.get_nodes()).difference(set(a.keys()))) == 1
        cond2 = len(set(self.get_nodes()).difference(set(b.keys()))) == 1
        cond3 = set() == set(a.keys()).difference(self.get_nodes())
        cond4 = set() == set(b.keys()).difference(self.get_nodes())
        cond5 = set((1,)) == set(a.values())
        cond6 = set((1,)) == set(b.values())
        if not all((cond1, cond2, cond3, cond4, cond5, cond6)):
            messages = []
            messages.append( "nodes without outedges %s" \
                    %( set(self.get_nodes()).difference((*(a.keys()),)) ))
            messages.append( "nodes without inedges %s" \
                    %( set(self.get_nodes()).difference((*(b.keys()),)) ))
            q3 = set(a.keys()).difference(self.get_nodes())
            q4 = set(b.keys()).difference(self.get_nodes())
            q5 = [node for node, count in a.items() if count!=1 ]
            qq5 = [ [(a,b) for a,b,label in self.get_edges_with_labels()\
                        if label=="next" and a==node] for node in q5]
            q6 = [node for node, count in b.items() if count!=1 ]
            qq6 = [ [(a,b) for a,b,label in self.get_edges_with_labels()\
                        if label=="next" and b==node] for node in q6]
            raise Exception( *messages, q3, q4, qq5, qq6 )
        return all((cond1, cond2, cond3, cond4))

