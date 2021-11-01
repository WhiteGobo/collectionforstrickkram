import networkx as _netx
from .. import strickgraph as mod_strickgraph

class strick_datacontainer():
    """Groundclass for fabric. Support for node and edges equivalent to fabric.

    :todo: only concentrate on methods, which equal a graph representation
    :todo: methods to be outsourced: get_rows, get_borders, get_connected_nodes,
            get_nodes_near_nodes, get_startside, find_following_row, 
            give_next_node_to, get_sidemargins_indices, get_sidemargins
    :todo: isvalid should me a method which works not only for strickgraphs
    """
    def __init__( self, nodeattributes, edgelabels ):
        self.__datacontainer = _netx.MultiDiGraph()
        for node, data in nodeattributes.items():
            self.__datacontainer.add_node( node, **data )
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
        return self._get_nodeattr( "stitchtype" )
    def get_nodeattr_side( self ):
        return self._get_nodeattr( "side" )
    def get_nodeattr_alternativestitchtype( self ):
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
        """Needed for verbesserer"""
        return tuple( (e[0], e[1], e[-1]["edgetype"]) \
                        for e in self.__datacontainer.edges( data=True ) )
        #subgraph = self.subgraph( set(self.nodes())-{"start", "end"})
        subgraph = self.subgraph( set(self.get_nodes()) )
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
        firststitch = self.get_startstitch()
        endstitch = self.get_endstitch()
        while firststitch != endstitch:
            currentrow = self.find_following_row( firststitch )
            rows.append( currentrow )
            if currentrow[ -1 ] == endstitch:
                break
            firststitch = self.give_next_node_to( currentrow[-1] )
        if presentation_type in mod_strickgraph.machine_terms:
            #tmprows = [] #dont need this
            node_side = _netx.get_node_attributes( self.__datacontainer, "side" )
            for row in rows:
                if node_side[ row[0] ] == "right":
                    pass
                else:
                    row.reverse()
                #tmprows.append( row )
            #rows = tmprows
        elif presentation_type in mod_strickgraph.handknitting_terms:
            pass
        else:
            raise mod_strickgraph.WrongTermError("get_rows can only print "\
                            +"in handknitting or" \
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
        :rtype nodelist: Tuple[ Hashable ]
        """
        #asd = self.give_real_graph()
        helpgraph = _netx.Graph()
        helpgraph.add_nodes_from( self.get_nodes() )
        helpgraph.add_edges_from( [e[:2] for e in self.get_edges_with_labels()] )
        nearthings = set( nodelist )
        for a,b in _netx.all_pairs_dijkstra_path( helpgraph,cutoff=maxdistance):
            if a in nodelist:
                nearthings.update( b.keys() )
        return tuple( nearthings )

    def get_startside( self ):
        """Get startside"""
        #firststitch = self.give_next_node_to( "start" )
        firststitch = self.get_startstitch()
        #endstitch = self.get_endstitch()
        firstrow = self.find_following_row( firststitch )
        nodeattr = _netx.get_node_attributes( self.__datacontainer, "side" )
        try:
            return nodeattr[ firstrow[0] ]
        except Exception as err:
            raise Exception( nodeattr, firstrow, firststitch ) from err

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
        edges = self.__datacontainer.edges( node, data=True )
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
