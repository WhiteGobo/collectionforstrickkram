import time
from ..strickgraph import strickgraph
from ..strickgraph.load_stitchinfo import myasd as glstinfo


def myfoo( linetype_out, linetype_in, upedges_out, upedges_in, changedline_id ):
    a = time.time()
    downedges = [ None, *upedges_out ]
    upedges = [ *upedges_out, None ]
    allinfo = zip( linetype_out, downedges, upedges )
    less_graph_man = [ s.create_example_row( down, up ) \
                                for s, down, up in allinfo ]
    less_graph = strickgraph.from_manual( less_graph_man, glstinfo, \
                                            manual_type="machine" )
    downedges = [ None, *upedges_in ]
    upedges = [ *upedges_in, None ]
    allinfo = zip( linetype_in, downedges, upedges )
    great_graph_man = [ s.create_example_row( down, up ) \
                                for s, down, up in allinfo ]
    great_graph = strickgraph.from_manual( great_graph_man, glstinfo, \
                                            manual_type="machine" )
    print( less_graph.to_manual( glstinfo,manual_type="machine" ), \
                great_graph.to_manual(glstinfo, manual_type="machine"))
    ##input("continue?")

    if linetype_out[0] == linetype_in[1]:
        startnode = (0,0)
    else:
        startnode = (len( linetype_out )-1, 0)
    mytime = time.time()
    difference_graph1, difference_graph2, c = \
                twographs_to_replacement( less_graph, great_graph, startnode )
    linenodes_graph1 = [ node for node in less_graph.get_rows()[0] \
                        if node in difference_graph1 ]
    print( time.time() - mytime )
    translator = { nodeA: nodeB for nodeA, nodeB in c }
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
    leftside_indices, rightside_indices \
                        = less_graph.get_sidemargins_indices()
    changed_row = rows[ changedline_id ]
    left_index = leftside_indices[ changedline_id ]
    right_index = rightside_indices[ changedline_id ]
    leftside_nodes = list(zip( changed_row[:left_index], range(left_index), ))
    rightside_nodes = list(zip( changed_row[right_index:], range(right_index, 0),  ))
    rightside_nodes.reverse()
    lessgraph_difference_line = [ node \
                for node in less_graph.get_rows()[ changedline_id ] \
                if node in difference_graph1 ]

    greatgraph_difference_line = [ node \
                for node in great_graph.get_rows()[ changedline_id ] \
                if node in difference_graph2 ]
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
        except Exception as err:
            pass
        try:
            startnode1_right, rightindex \
                = list( (node, index) for node,index in rightside_nodes\
                if node in asdf ).pop(0)
            startnode2_right = translator[ startnode1_right ]
        except Exception as err:
            pass

def generate_verbesserer_from_given_strickgraphs( graph1, graph2, \
                                    subnodelist_left1, subnodelist_left2, \
                                    subnodelist_right1, subnodelist_right2):
            from extrasfornetworkx import generate_replacement_from_graphs
            nodelabels1 = graph1.get_nodeattributelabel()
            edgelabels1 = graph1.get_edgeattributelabels()
            nodelabels2 = graph2.get_nodeattributelabel()
            edgelabels2 = graph2.get_edgeattributelabels()
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

            repl1, repl2, common_nodes = generate_replacement_from_graphs(\
                                                nodelabels1, edgelabels1,\
                                                nodelabels2, edgelabels2, \
                                                startnode, startnode )
            print("\n\n")
            print( "repl1:", repl1, "\n", "repl2: ", repl2, "\n\n", common_nodes)
            print( "needed time: %.3f" %( time.time() - starttime ))

            #difference = somesomething( graph1, graph2 )


def twographs_to_replacement( graph1, graph2, startnode ):
    from extrasfornetworkx import generate_replacement_from_graphs
    nodelabels1 = graph1.get_nodeattributelabel()
    edgelabels1 = graph1.get_edgeattributelabels()
    nodelabels2 = graph2.get_nodeattributelabel()
    edgelabels2 = graph2.get_edgeattributelabels()
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

    repl1, repl2, common_nodes = generate_replacement_from_graphs(\
                                        nodelabels1, edgelabels1,\
                                        nodelabels2, edgelabels2, \
                                        nodetrans1[startnode], \
                                        nodetrans2[startnode] )
    antitrans1 = { b:a for a,b in nodetrans1.items() }
    antitrans2 = { b:a for a,b in nodetrans2.items() }
    return tuple( antitrans1[ node ] for node in repl1 ), \
            tuple( antitrans2[ node ] for node in repl2 ), \
            tuple( (antitrans1[n1], antitrans2[n2]) for n1, n2 in common_nodes )
