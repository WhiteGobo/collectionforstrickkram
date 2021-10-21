from ..strickgraph import strickgraph
from ..stitchinfo import basic_stitchdata as glstinfo

class NoLeftRightFound( Exception ):
    pass

def myfoo( linetype_out, linetype_in, upedges_out, upedges_in, changedline_id ):
    """

    :raises: NoLeftRightFound
    """
    less_graph = create_graph_from_linetypes( linetype_out, upedges_out )
    great_graph = create_graph_from_linetypes( linetype_in, upedges_in )
    from ..verbesserer.class_side_alterator import sidealterator
    #print( less_graph.to_manual( glstinfo,manual_type="machine" ), \
    #            great_graph.to_manual(glstinfo, manual_type="machine"))
    #input("continue?")

    if linetype_out[0] == linetype_in[1]:
        startnode = (0,0)
    else:
        startnode = (len( linetype_out )-1, 0)

    return sidealterator( less_graph, great_graph, startnode, changedline_id )

    difference_graph1, difference_graph2, c = \
                twographs_to_replacement( less_graph, great_graph, startnode  )
    translator = { nodeA: nodeB for nodeA, nodeB in c }
    leftnodes1, leftnodes2, startnode1_left, leftindex, \
                rightnodes1, rightnodes2, startnode1_right, rightindex \
                = separate_wholegraphs_to_leftright_insulas( \
                        difference_graph1, difference_graph2, translator, \
                        less_graph, great_graph, changedline_id )

    startnode2_left = translator[ startnode1_left ]
    startnode2_right = translator[ startnode1_right ]
    return generate_verbesserer_from_given_strickgraphs( \
                                less_graph, great_graph, \
                                leftnodes1, leftnodes2, \
                                startnode1_left, startnode2_left, leftindex, \
                                rightnodes1, rightnodes2, \
                                startnode1_right, startnode2_right, rightindex )


def create_graph_from_linetypes( linetypes, upedges ):
    """Seems to be a double to thing from create_example_strickgraphs

    :todo: undouble this method
    """
    downedges = [ None, *upedges ]
    upedges = [ *upedges, None ]
    allinfo = zip( linetypes, downedges, upedges )
    graph_man = [ s.create_example_row( down, up ) \
                                for s, down, up in allinfo ]
    graph = strickgraph.from_manual( graph_man, glstinfo, manual_type="machine")
    return graph

def separate_wholegraphs_to_leftright_insulas( \
                        difference_graph1, difference_graph2, translator, \
                        less_graph, great_graph, \
                        changedline_id ):
    """

    :raises: NoLeftRightFound
    """
    linenodes_graph1 = [ node for node in less_graph.get_rows()[0] \
                        if node in difference_graph1 ]
    #half the graph
    rows = less_graph.get_rows()
    rowlength = sum( len(row) for row in rows ) / len(rows)
    isonleftside = lambda node: node[1] < rowlength
    less_graph_nodes = less_graph.give_real_graph().nodes()
    great_graph_nodes = great_graph.give_real_graph().nodes()

    #find left and right side to replace with insulas
    connected_insulas = less_graph.get_connected_nodes( \
                                                    difference_graph1 )
    connected_insulas2 = great_graph.get_connected_nodes( \
                                                    difference_graph2 )
    ## This here helps for finding two corresponding conninsulas
    ## saved in maximal_shared_nodes
    #connected_insulas = tuple(tuple(nodeset) for nodeset in connected_insulas)
    #connected_insulas2= tuple(tuple(nodeset) for nodeset in connected_insulas2)
    #get_number_shared_nodes = lambda n1, n2: len( set(n2)\
    #                                            .intersection( translator[n] \
    #                                            for n in n1 if n in translator) )
    #decor = lambda n1, func: lambda n2: func( n1, n2 ) #reduce to one input
    #fetch_correspond = lambda n1:  \
    #        max( connected_insulas2, key=decor( n1, get_number_shared_nodes) )
    #maximal_shared_nodes = tuple( (n1,fetch_correspond( n1 )) \
    #                                    for n1 in connected_insulas )
    #from collections import Counter
    #assert max(Counter(pair[0] for pair in maximal_shared_nodes).values())==1,\
    #                "connected insulas are double corresponding"
    #assert max(Counter(pair[1] for pair in maximal_shared_nodes).values())==1,\
    #                "connected insulas are double corresponding"

    

    leftside_indices, rightside_indices \
                        = less_graph.get_sidemargins_indices()
    changed_row = rows[ changedline_id ]
    left_index = leftside_indices[ changedline_id ]
    right_index = rightside_indices[ changedline_id ]
    leftside_nodes = list(zip( changed_row[:left_index], range(left_index), ))
    rightside_nodes = list(zip( changed_row[right_index:], range(right_index, 0), ))
    rightside_nodes.reverse()
    lessgraph_difference_line = [ node \
                for node in less_graph.get_rows()[ changedline_id ] \
                if node in difference_graph1 ]

    greatgraph_difference_line = [ node \
                for node in great_graph.get_rows()[ changedline_id ] \
                if node in difference_graph2 ]

    leftnodes1: list
    leftnodes2: list
    rightnodes1: list
    rightnodes2: list
    leftindex: int
    rightindex: int
    for asdf in connected_insulas:
        for qwer in connected_insulas2:
            if any( translator[q] in qwer \
                            for q in asdf if q in translator.keys() ):
                break
        nearnodes = less_graph.get_nodes_near_nodes( asdf )
        nearnodes2 = great_graph.get_nodes_near_nodes( qwer )
        try:
            startnode1_left, leftindex \
                = list( (node, index) for node, index in leftside_nodes\
                if node in asdf ).pop(0)
            startnode2_left = translator[ startnode1_left ]
            leftnodes1 = nearnodes
            leftnodes2 = set( translator[n] for n in nearnodes if n in translator)\
                            .union(qwer)
        except Exception as err:
            pass
        try:
            startnode1_right, rightindex \
                = list( (node, index) for node,index in rightside_nodes\
                if node in asdf ).pop(0)
            startnode2_right = translator[ startnode1_right ]
            rightnodes1 = nearnodes
            rightnodes2 = set( translator[n] for n in nearnodes if n in translator)\
                            .union(qwer)
        except Exception as err:
            pass
    try:
        return leftnodes1, leftnodes2, startnode1_left, leftindex, \
                rightnodes1, rightnodes2, startnode1_right, rightindex
    except NameError as err:
        raise NoLeftRightFound() from err


def generate_verbesserer_from_given_strickgraphs( graph1, graph2, \
                                subnodelist_left1, subnodelist_left2, \
                                startnode1_left, startnode2_left, leftindex, \
                                subnodelist_right1, subnodelist_right2, \
                                startnode1_right, startnode2_right, rightindex):
    """Function for creation of alterator. Is mist liekly obsolent because of 
    generator of class_side_alterator
    
    :todo: ueberpruefe if this is bsolete
    """
    graph1_left = graph1.subgraph( subnodelist_left1 )
    graph2_left = graph2.subgraph( subnodelist_left2 )
    graph1_right = graph1.subgraph( subnodelist_right1 )
    graph2_right = graph2.subgraph( subnodelist_right2 )
    from extrasfornetworkx import generate_replacement_from_graphs
    nodelabels1 = graph1_left.get_nodeattributes()
    edgelabels1 = graph1_left.get_edgeattributelabels()
    nodelabels2 = graph2_left.get_nodeattributes()
    edgelabels2 = graph2_left.get_edgeattributelabels()
    nodetrans1 = { n:i for i, n in enumerate( nodelabels1.keys() )}
    nodetrans2 = { n:i for i, n in enumerate( nodelabels2.keys() )}
    nodelabels1 = { nodetrans1[ node ]: label \
                        for node, label in nodelabels1.items() }
    edgelabels1 = [ (nodetrans1[v1], nodetrans1[v2], label) \
                        for v1, v2, label in edgelabels1 ]
    nodelabels2 = { nodetrans2[ node ]: label \
                        for node, label in nodelabels2.items() }
    edgelabels2 = [ (nodetrans2[v1], nodetrans2[v2], label) \
                        for v1, v2, label in edgelabels2 ]

    from ..verbesserer.verbesserer_class import strickalterator
    asdf = strickalterator.from_graph_difference(
                                        nodelabels1, edgelabels1,\
                                        nodelabels2, edgelabels2, \
                                        nodetrans1[startnode1_left], \
                                        nodetrans2[startnode2_left] )
    return asdf
    
    #repl1, repl2, common_nodes = generate_replacement_from_graphs(\
    #                                    nodelabels1, edgelabels1,\
    #                                    nodelabels2, edgelabels2, \
    #                                    nodetrans1[startnode1_left], \
    #                                    nodetrans2[startnode2_left] )

    #print("\n\n")
    #print( "repl1:", repl1, "\n", "repl2: ", repl2, "\n\n", common_nodes)

    #difference = somesomething( graph1, graph2 )


def twographs_to_replacement( graph1, graph2, startnode ):
    """helper function, might be obsolete.

    :todo: check if this is obsolete
    """
    from extrasfornetworkx import generate_replacement_from_graphs
    nodelabels1 = graph1.get_nodeattributelabel()
    edgelabels1 = graph1.get_edgeattributelabels()
    nodelabels2 = graph2.get_nodeattributelabel()
    edgelabels2 = graph2.get_edgeattributelabels()
    nodetrans1 = { n:i for i, n in enumerate( nodelabels1.keys() )}
    nodetrans2 = { n:i for i, n in enumerate( nodelabels2.keys() )}
    antitrans1 = { b:a for a,b in nodetrans1.items() }
    antitrans2 = { b:a for a,b in nodetrans2.items() }
    nodelabels1 = { nodetrans1[ node ]: label \
                        for node, label in nodelabels1.items() }
    edgelabels1 = [ (nodetrans1[v1], nodetrans1[v2], label) \
                        for v1, v2, label in edgelabels1 ]
    nodelabels2 = { nodetrans2[ node ]: label \
                        for node, label in nodelabels2.items() }
    edgelabels2 = [ (nodetrans2[v1], nodetrans2[v2], label) \
                        for v1, v2, label in edgelabels2 ]

    repl1, repl2, common_nodes = generate_replacement_from_graphs(\
                                        nodelabels1, edgelabels1,\
                                        nodelabels2, edgelabels2, \
                                        nodetrans1[startnode], \
                                        nodetrans2[startnode] )
    return tuple( antitrans1[ node ] for node in repl1 ), \
            tuple( antitrans2[ node ] for node in repl2 ), \
            tuple( (antitrans1[n1], antitrans2[n2]) for n1, n2 in common_nodes )
