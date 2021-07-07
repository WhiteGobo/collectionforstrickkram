import networkx as netx

class strickgraph( netx.MultiDiGraph ):
    def __init__( self, *args, **argv ):
        self.supergraph = self
        super().__init__( *args, **argv )

    #@classmethod
    #def from_gridgraph( cls, graph, firstrow, stitchinfo, startside="right" ):
    #    return fromgrid.create_strickgraph_from_gridgraph( graph, firstrow, \
    #                                                stitchinfo, startside )

    def give_real_graph( self ):
        return self.subgraph( set(self.nodes()).difference(["start", "end"]))

    def subgraph( self, *args, **argv ):
        tmpsubgraph = super().subgraph( *args, **argv )
        tmpsubgraph.supergraph = self
        return tmpsubgraph

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

    def to_manual( self, stitchinfo, manual_type="thread" ):
        return toknitmanual.tomanual( self, stitchinfo, manual_type)

    @classmethod
    def from_manual( cls, manual, stitchinfo, manual_type="thread", \
                                        startside="right", reversed=False ):
        from . import fromknitmanual as frmman
        return frmman.frommanual( manual, stitchinfo, manual_type, startside, reversed)


