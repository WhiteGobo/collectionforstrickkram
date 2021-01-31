"""
This module replaces a subgraph of a graph with another graph
via anchor points it should automaticly search for the searched subgraph and 
replace it.
it should load different sets of graph marked for replacement. The sets should 
contain the graph taht will come out of the replacement
The graphs should support weilfeilerlehmanhashing for comparing the subgraph
with the set
:todo: i think this module is obsolete
"""
import networkx as netx
from copy import copy

def create_pathforhashing( strickgraph, anchornode, \
                            edgeattribute="edgetype", \
                            nodeattributes=("stitchtype","side"), \
                            ):
    """
    Obsolete will be replaced from extrasfornetworkx.create_pathforhashing
    Creates apath list for reconstruction of a subgraph from an anchorpoint of
    a graph. 
    :param strickgraph: this should be a connected graph
    :type strickgraph: networkx.Graph-like
    :param anchornode: This node will be used as startpoint, when replacment
    :type anchornode: hashable, node in strickgraph
    :param nodeattribute: value of each node used for hashing
    :param edgeattribute: value of each edge used for hashing
    :todo: remove this, first insert Exception and test
    """
    print( "Obsolete will be replaced from extrasfornetworkx.create_pathforhashing" )
    path_to_search = []
    nodeattribute_on_path =[ get_node_attribute_tuple( strickgraph, anchornode,\
                                                    nodeattributes ) ]
    neighbours, nextpoint, edgeattribute_value = None,None,None
    visited = [ anchornode ]
    for j in range( 1, len(strickgraph.nodes()) ):
        neighbours = []
        i=0
        while len( neighbours ) == 0:
            lastpoint = visited[i]
            i = i-1
            neighbours = list(strickgraph.adj[ lastpoint ]) \
                        + list(strickgraph.pred[ lastpoint])
            neighbours = [ x for x in neighbours if x not in visited ]
        nextpoint = neighbours[0]
        visited.append( nextpoint )
        edges = find_all_edges_between( lastpoint, nextpoint, strickgraph )
        #strickgraph is always Digraph
        if edges[0][0] == lastpoint:
            edgedirection = "out"
        else:
            edgedirection = "in"
        edgeattribute_value = netx.get_edge_attributes( strickgraph, \
                                                edgeattribute )[(*edges[0],0)]
        nodeattribute_value = get_node_attribute_tuple( strickgraph, \
                                                nextpoint, nodeattributes )
        #nodeattribute_value = netx.get_node_attributes( strickgraph,\
        #                                            nodeattribute)[ nextpoint ]
        path_to_search.append( (visited.index(lastpoint), edgedirection, edgeattribute_value, visited.index(nextpoint)) )
        nodeattribute_on_path.append( nodeattribute_value )
    return path_to_search, nodeattribute_on_path, visited


class _followpath_helper():
    def __init__( self, strickgraph, path, nodeattributes, nodeattributenames, \
                                        processed_nodeattributes=None, \
                                        visited=None, startnode=None ):
        """
        uses visited for nodeidentification. on init need the first node
        as visited = {0:firstnode}
        :param nodeattributes: list of tuples
        :todo: replace visited with dictionary with ints as keys
        """
        if startnode != None:
            visited = {0: startnode}
        elif len(visited)==0:
            raise Exception( "no starting point given to follow path" )

        self.visited = dict(visited) #copy
        self.strickgraph = strickgraph
        self.path = list(path) #copy
        self.nodeattributes, self.nodeattributenames = \
                    self.process_nodeattributes( \
                                    nodeattributes, nodeattributenames, \
                                    processed_nodeattributes)
        print( self.nodeattributes )
        self.found=[]

    def work( self ):
        loop = True
        while loop and len(self.path) > 0:
            loop = self.cycle()
        if len(self.path) == 0:
            translator = dict(self.visited)
            return self.found \
                    + [([ self.visited[x] for x in self.visited ], translator) ]
        else:
            return self.found

    def process_nodeattributes( self, nodeattributes, nodeattributenames, \
                                    processed_nodeattributes ):
        if None == processed_nodeattributes:
            returnnodeattributenames = nodeattributenames
            returnnodeattributes = {}
            for nodeattribute in nodeattributenames:
                i = nodeattributenames.index( nodeattribute )
                returnnodeattributes[nodeattribute] \
                        = [ x[i] for x in nodeattributes ]
        else:
            returnnodeattributes = processed_nodeattributes
            returnnodeattributenames = list( processed_nodeattributes.keys() )
        return returnnodeattributes, returnnodeattributenames

    def cycle( self ):
        """
        follow the path with the first possible option every time
        if multiple options are possible to follow the given path, create a new
        helper to follow that path
        """
        nextpath = self.path.pop(0)
        filtered_edges, partners = self.find_nextpossible_edges( nextpath )

        if len(filtered_edges) == 0:
            return False
        for i in range(1,len(filtered_edges)):
            print("try edge:", filtered_edges[i] )
            nextnode = partners[ filtered_edges[i] ]
            tmpfound = self.startnewhelper( nextnode, int(nextpath[3]) )
            self.found = self.found + tmpfound
        print("return to edge:", filtered_edges[0] )
        self.visited.update({ int(nextpath[3]): partners[ filtered_edges[0] ] })

        if not self.validate_nodes_to_nodeattributes():
            return False
        return True

    def startnewhelper( self, newnode, newnodeposition ):
        """
        :todo: remove exception catches
        """
        newvisited = copy( self.visited )
        newvisited.update({ newnodeposition : newnode})
        try:
            newhelper = _followpath_helper( self.strickgraph, \
                            list(self.path),\
                            #self.nodeattributes, self.nodeattributenames,\
                            None, None, \
                            processed_nodeattributes= self.nodeattributes, \
                            visited=newvisited )
            return newhelper.work()
        except Exception as err:
            err.args = ( *err.args, self.nodeattributes )
            raise err

    def find_nextpossible_edges( self, nextpath ):
        """
        :todo: remove exception catching at the end
        """
        firstnode = self.visited[ int(nextpath[0]) ]
        if nextpath[1] == "in":
            edges = self.strickgraph.in_edges( firstnode )
            partners = {x:x[0] for x in edges}
        elif nextpath[1] == "out":
            edges = self.strickgraph.edges( firstnode )
            partners = {x:x[1] for x in edges}
        edgeattr = netx.get_edge_attributes( self.strickgraph, "edgetype" )
        filtered_edges = []
        for tmpedge in edges:
            for i in range(self.strickgraph.number_of_edges( *tmpedge )):
                filtered_edges.append( (*tmpedge,i) )
                partners.update( {( *tmpedge, i ): partners[ tmpedge ]} )
        filtered_edges = [x for x in filtered_edges if edgeattr[x]==nextpath[2]]
        for attr in self.nodeattributenames:
            i = self.nodeattributenames.index( attr )
            mynodeattr = netx.get_node_attributes( self.strickgraph, attr )
            try:
                filtered_edges = [ x for x in filtered_edges \
                        if mynodeattr[ partners[x] ] \
                        ==self.nodeattributes[ attr][ int(nextpath[3]) ]]
            except Exception as err:
                err.args = ( *err.args, int(nextpath[3]), \
                                self.nodeattributes[attr] )
                raise err
        return filtered_edges, partners

    def validate_nodes_to_nodeattributes( self ):
        valid = True
        realattr = self.strickgraph.nodes( data=True )
        for node in self.visited:
            realnode = self.visited[ node ]
            for attrname in self.nodeattributenames:
                tmpvalid = \
                        realattr[ realnode ][ attrname ] \
                        == self.nodeattributes[ attrname ][ node ]
                valid = valid and tmpvalid
        return valid
            
            


        

def follow_cached_path( strickgraph, startnode, path, nodeattributes_on_path):
    """
    Obsolete will be replaced from extrasfornetworkx.create_pathforhashing
    return all subgraphs as node-sets matching in given graph
    starting from startnode follows a path directed by path in the graph
    checks if nodeattributes of the path are equal to the nodeattributes_on_path
    :param path: l list of tuple which gives the corresponding(to attribute) 
            node if edge is in or out and the second node, both nodes correspond
            to the nodeattributes_on_path-list
    :param bideattributes_on_path: gives the nodeaatrbiute of a found node
    :type strickgraph: networkx.DiGraph-like
    :type startnode: hashable
    :type path: list(x*tuple( int, str, str, int )),
    :param path: (firstnode, 'out/in', 'edgeattribute', secondnode)
    :type nodeattributes_on_path: list( str )
    :rtype: subgraphs
    :todo: remove this, first insert Exception and test
    """
    print("Obsolete will be replaced from extrasfornetworkx.create_pathforhashing")
    myhelper = _followpath_helper( strickgraph, path, nodeattributes_on_path, \
                                ["stitchtype", "side"], startnode = startnode )
    return myhelper.work()
    foundsubgraphs = myhelper.work()
    translator = list(myhelper.visited)
    foundsubgraphs = [ strickgraph.subgraph( nodelist ) for nodelist in foundsubgraphs ]
    return [(foundsubgraphs[0], translator),]


def find_all_edges_between( first, second, graph ):
    """
    :type graph: networkx.DiGraph
    :todo: rewrite
    """
    edges1 = [ x for x in graph.edges( first ) if x[1]==second ]
    edges2 = [ x for x in graph.edges( second ) if x[1]==first ]
    return edges1 + edges2

def get_node_attribute_tuple( graph, node, nodeattributes ):
    tmplist = []
    for nodeattribute in nodeattributes:
        tmp_value = netx.get_node_attributes( graph, nodeattribute)[ node ]
        tmplist.append( tmp_value )
    return tuple( tmplist )
    nodeattribute_value = tuple( tmplist )
    nodeattribute_on_path = [ nodeattribute_value ]
