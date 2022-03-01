"""Tools for copy for custom alterators

:todo: better description
"""

import networkx as netx
from extrasfornetworkx import alterator
from typing import Hashable, Iterable, Tuple
import itertools as it

def filter_translators( *args, **kwargs ):
    raise NotImplementedError()

def separate_to_2_subgraphpairs( translator, neighbours1, neighbours2, \
                                        number_of_alterations = 2 ):
    """Each graph will be split into 2 graphs and each part
    will correspond to a part from the other graph. So that some
    node n1 from a part will be translatable to the corresponding 
    node n2 (translator[n1]=n2).
    The graphs will be split so, that the distance between 
    the alterating parts of the whole graphs will have a maximal
    distance to the border between the two parts of a single graph.
    """

    difference_graph1 = [ n for n in neighbours1 \
                        if n not in translator.keys()]
    difference_graph2 = [ n for n in neighbours2 \
                        if n not in translator.values()]
    border1, border2 = get_border( difference_graph1, \
                        difference_graph2, translator,\
                        neighbours1, neighbours2 )
    alteration_nodes1 = list( it.chain( difference_graph1, border1 ) )
    alteration_nodes2 = list( it.chain( difference_graph2, border2 ) )

    Node = Hashable
    Nodes1 = Iterable[ Node ]
    """list of nodes from graph1"""
    Nodes2 = Iterable[ Node ]
    """list of nodes from graph2"""
    Insulapair = Tuple[ Nodes1, Nodes2 ]
    """pair of nodelists from graph 1 and 2 
    which are touching each other
    """
                #= determine_connected_insulas( \
    insulapairs: Iterable[ Insulapair ] \
                = determine_insula_pairs(
                        alteration_nodes1, alteration_nodes2, \
                        neighbours1, neighbours2, translator )

    Nodealterationpair = Tuple[ Nodes1, Nodes2 ]
    """pair of nodelists from graph 1 and 2 
    which are used for alteration
    """
    reduced_alterationnode_pairs: Iterable[Nodealterationpair]\
             = pack_insulas_to_alterationnodes( \
                        insulapairs, neighbours1, \
                        number_of_alterations )

    Subgraph_pair = Iterable[ Tuple[ Nodes1, Nodes2 ] ]
    graph1_parts = cut_to_subgraph( [ n1 for n1, _ in reduced_alterationnode_pairs ], neighbours1 )
    graph2_parts = cut_to_subgraph( [ n2 for _, n2 in reduced_alterationnode_pairs ], neighbours2 )
    subgraph_pairs: Iterable[ Subgraph_pair ] \
            = list( zip( graph1_parts, graph2_parts ) )
    #subgraph_pairs: Iterable[ Subgraph_pair ] \
            #         = cut_to_subgraphs( \
            #            reduced_alterationnode_pairs,\
            #            neighbours1, neighbours2 )
    return subgraph_pairs

def create_single_alterator( nodeattr1, edgeattr1, nodeattr2, \
                                    edgeattr2, nodes1, nodes2, \
                                    translator, startpoint, directional ):
    filter_nodes = lambda attr, nodes: { n:a for n, a in attr.items()\
                            if n in nodes }
    filter_edges = lambda edges, nodes: [ (v1, v2, attr) \
                            for v1, v2, attr in edges \
                            if all( v in nodes for v in (v1, v2) )]
    part_nodeattr1 = filter_nodes( nodeattr1, nodes1 )
    part_nodeattr2 = filter_nodes( nodeattr2, nodes2 )
    part_edgeattr1 = filter_edges( edgeattr1, nodes1 )
    part_edgeattr2 = filter_edges( edgeattr2, nodes2 )
    part_alterator = alterator.with_common_nodes( \
                            part_nodeattr1, part_edgeattr1, \
                            part_nodeattr2, part_edgeattr2, \
                            translator, startpoint, \
                            directional = directional )
    return part_alterator


def get_border( uncommon_nodes1, uncommon_nodes2, translator, neighbours1, neighbours2 ):
    assert all( n in translator.values() or n in uncommon_nodes2 for n in neighbours2.keys() )
    assert all( n in translator.keys() or n in uncommon_nodes1 for n in neighbours1.keys() )

    subnodes = [ (1,n) for n in uncommon_nodes1 ]
    subnodes.extend( [ (2,n) for n in uncommon_nodes2 ] )
    tnode = lambda x: (2,translator[x]) if x in translator else (1,x)
    tlist = lambda X: [ tnode(x) for x in X ]
    neighs = { tnode(n): tlist(nlist) \
                    for n, nlist in neighbours1.items() }
    neighs.update( { (2,n): [(2,k) for k in nlist] \
                    for n, nlist in neighbours2.items() } )

    tmp = it.chain.from_iterable( neighs[n] for n in subnodes )
    border2 = list( set( n for n in tmp if n not in subnodes ) )
    antitrans = { b:a for a,b in translator.items() }
    border1 = [ antitrans[n[1]] for n in border2 ]
    border2 = [ n for _, n in border2 ]
    return border1, border2


def neighs_from_edges( edges ):
    neighbours = {}
    for e in edges:
        v1, v2 = e[ :2 ]
        neighbours.setdefault( v1, list() ).append( v2 )
        neighbours.setdefault( v2, list() ).append( v1 )
    return neighbours
    

def get_insulas( subnodes, neighbours ):
    helpergraph = netx.Graph( neighbours )
    for node in list(helpergraph.nodes):
            if node not in subnodes:
                    helpergraph.remove_node( node )
    comp_list = list( netx.connected_components( helpergraph ) )
    return comp_list

def determine_insula_pairs( subnodes1, subnodes2, neighbours1, neighbours2, translator ):
    subnodes1, subnodes2 = list(subnodes1), list(subnodes2)
    insulas1 = get_insulas( subnodes1, neighbours1 )
    insulas2 = get_insulas( subnodes2, neighbours2 )

    translate_nodes = lambda X: tuple( translator[n] \
                                    for n in X \
                                    if n in translator )
    isconnected = lambda X, Y: any( n in Y for n in translate_nodes(X) )
    retrieve_connected = lambda X: [ (2,j) \
                            for j,Y in enumerate(insulas2) \
                            if isconnected(X,Y) ]
    connected = { (1,i): retrieve_connected( X ) for i,X in enumerate(insulas1) }
    connected.update( {(2,j):[] for j, Y in enumerate(insulas2)} )
    helpergraph = netx.Graph( connected )
    pairs = []
    for nodelist_indices in netx.connected_components( helpergraph ):
            nodes1 = set()
            nodes2 = set()
            for graph_index, insula_index in nodelist_indices:
                    if graph_index == 1:
                            nodes1.update( insulas1[ insula_index ] )
                    elif graph_index == 2:
                            nodes2.update( insulas2[ insula_index ] )
            pairs.append( (list(nodes1), list(nodes2)) )
    return pairs

def _distance_between_insulas( insulas, neighbours ):
        insulanodes = list( it.chain.from_iterable( insulas ) )
        dist_graph = netx.Graph()
        for v1, v2list in neighbours.items():
            for v2 in v2list:
                tmpdistance = 0 if all(v in insulanodes for v in (v1, v2)) else 1
                dist_graph.add_edge( v1, v2, d=tmpdistance )
        return dict( netx.shortest_path_length( dist_graph, weight="d" ))


def pack_insulas_to_alterationnodes( insulapairs, neighbours1, \
                                    number_of_alterations ):
    if len(insulapairs) < number_of_alterations:
        raise ValueError( "not enough insulas for alterations", \
                            insulapairs,number_of_alterations)
    insulanodes1 = [ q1 for q1, q2 in insulapairs ]
    dist_between_nodes = _distance_between_insulas( insulanodes1, neighbours1 )
    insulagraph = netx.Graph() #nodes represent insulas
    for i, source_insula in enumerate( insulanodes1 ):
        sourcenode = iter( source_insula ).__next__()
        for j, target_insula in enumerate( insulanodes1 ):
            if i != j:
                targetnode = iter( target_insula ).__next__()
                opt = { "weight": dist_between_nodes[ sourcenode ]\
                                                       [ targetnode ]}
                insulagraph.add_edge( i, j, **opt )
    q = netx.minimum_spanning_tree( insulagraph, weight='weight' )
    edge_length = { (v1, v2): data["weight"] \
                        for v1, v2, data in q.edges(data=True) }
    longest_edges = sorted( edge_length, key=edge_length.__getitem__, reverse=True )
    #minimum is 5 or border of alterator will make problems
    insula_sourcenodes = [ iter( ins ).__next__() for ins in insulanodes1 ]

    #myhelper = netx.shortest_path( dist_graph, weight="d" )
    helperedges = [ (insula_sourcenodes[v1], insula_sourcenodes[v2]) \
                    for v1, v2 in q.edges() ]
    foo = lambda nlist: ( nlist, [ antitrans.get(n, None) for n in nlist])

    for i in range( number_of_alterations-1 ):
        longest_edge = longest_edges[i]
        assert edge_length[ longest_edge ] >= 5 
        q.remove_edge( *longest_edge )
    insulagroups = list( netx.connected_components( q ) )
    assert len( insulagroups ) == number_of_alterations
    uncommon_node_packs = [ (set(),set()) for i in range( number_of_alterations ) ]
    for i, insulapair in enumerate( insulapairs ):
            n1, n2 = insulapair
            try:
                uncommon_node_packs[i][0].update( n1 )
                uncommon_node_packs[i][1].update( n2 )
            except Exception as err:
                raise Exception( uncommon_node_packs, i ) from err
    return uncommon_node_packs

def cut_to_subgraph( alteration_parts, neighbours ):
    """Border of alteration_pairs must be in those pair. Borders are 
    shared nodes neighbouring to nodes that are only in one graph.

    :param neighbours: every node in graph
    :type neighbours: Dict[ Node, Iterable[ Node ]]
    :param alteration_parts: Pairlist of nodes with 
            all alteration nodes and borders.
    :type alteration_parts: Iterable[ Iterable[ Node ] ]
    :returns: nodes with every node from graph.
    :rtype: Iterable[ List[ Node ] ]
    """
    dist_graph = netx.Graph( neighbours )
    myhelper = dict( netx.shortest_path_length( dist_graph ) )
    all_distances = []
    for i, nodes in enumerate( alteration_parts ):
        dist = {}
        all_distances.append( dist )
        for target in neighbours:
            tmp_dist = min( myhelper[n][target] for n in nodes )
            dist[ target ] = tmp_dist
    number = len( alteration_parts )
    cutting = [ [] for i in range( number ) ]
    for target in neighbours:
        distkey = lambda i: all_distances[i][target]
        index = min( range(number), key=distkey )
        cutting[ index ].append( target )
    return cutting


