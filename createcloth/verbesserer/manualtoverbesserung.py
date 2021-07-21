from ..strickgraph.fromknitmanual import frommanual
from ..strickgraph.strickgraph_base import get_neighbours_from
import networkx as netx
import math
from ..strickgraph.strickgraph_replacesubgraph import create_pathforhashing
from . import xml_config
import xml.etree.ElementTree as ET
#from lxml import etree as ET
from extrasfornetworkx import verbesserer

class manualtoverbesserung_Exception( Exception ):
    pass

def main( manual_old, manual_new, start_at="bottomleft", \
            nodes_to_consider=None, start_side="right"):
    """
    generates everything i need for replacing a subgraph
    :param nodes_to_consider: state which nodes should be searched for, when
                        replacing a subgraph. if none equals automated
    :type nodes_to_consider: none, networkx.graph or list
    :param manual_old: the graph where the subgraph is to be searched for
    :param manual_new: the target graph
    :param start_at: string to determine which node should be starting node for
                    the search later in the replacement
                    possible options are given by:
                        find_startpoint_dictionary.keys()
                    extra options can be added, see find_startpoint_dictionary
    :type start_at: str
    :todo: remake xml to contain which attributes are used in path generation
            currently there is no information that it used side and edgetype
            in pathinfo or nodetype in nodeinfo_onpath.
            THIS,     is clearly wrong:(
    """
    old_graph = frommanual( manual_old, startside = start_side, \
                                        manual_type="machine" )
    new_graph = frommanual( manual_new, startside = start_side, \
                                        manual_type="machine" )
    return verbesserer.from_graph_difference( \
                                            old_graph, new_graph, \
                                            "start", "start", \
                                            "edgetype", ["stitchtype", "side"] )
    nodes_subgraph_old, nodes_subgraph_new, same_nodes = \
                                        generate_replacement_from_graphs( \
                                                    old_graph, new_graph, \
                                                        nodes_to_consider )
    subgraph_old = old_graph.subgraph( nodes_subgraph_old )
    subgraph_new = new_graph.subgraph( nodes_subgraph_new )
    find_function = find_startpoint_dictionary[ start_at ]
    starting_point = find_function( subgraph_old )

    path, nodeinfo, translator = create_pathforhashing( subgraph_old,
                                                        starting_point )
    old_graph, new_graph, replacement_old, replacement_new = \
                                    replace_nodenames_for_samenames( \
                                            same_nodes, translator, \
                                            old_graph, new_graph )
    subgraph_old = None #is broken by replacement
    subgraph_new = None
    nodes_subgraph_old = replace_nodes_in_list( nodes_subgraph_old, \
                                            replacement_old )
    nodes_subgraph_new = replace_nodes_in_list( nodes_subgraph_new, \
                                            replacement_new )
    subgraph_old = old_graph.subgraph( nodes_subgraph_old )
    subgraph_new = new_graph.subgraph( nodes_subgraph_new )
    build_xmlElement( subgraph_old, subgraph_new, path, nodeinfo )

def replace_nodes_in_list( mylist, mymap ):
    tmplist = []
    for node in mylist:
        if node in mymap:
            tmplist.append( mymap[ node ] )
        else:
            tmplist.append( node )
    return tmplist

def build_xmlElement( old_graph, new_graph, path, nodeinfo, decode="utf8" ):
    """
    :todo: bother with xml namespaces
            overhaul the return statement
    """
    ET.register_namespace( "asd", xml_config.namespace )
    ET.register_namespace( "grml", "http://graphml.graphdrawing.org/xmlns" )
    ET.register_namespace( "xsi", "http://www.w3.org/2001/XMLSchema-instance" )
    oldgraphml = netx.generate_graphml( old_graph )
    oldgraphml = "\n".join( oldgraphml )
    oldgraph_xmlelement = ET.fromstring( oldgraphml )
    newgraphml = netx.generate_graphml( new_graph )
    newgraphml = "\n".join( newgraphml )
    newgraph_xmlelement = ET.fromstring( newgraphml )

    elemroot = ET.Element( xml_config.ersetzung )
    elemold = ET.SubElement( elemroot, xml_config.oldgraph )
    elemold.append( oldgraph_xmlelement )
    elemnew = ET.SubElement( elemroot, xml_config.newgraph )
    elemnew.append( newgraph_xmlelement )
    elemroot.append( pathoto_xmlelement( path ) )
    elemroot.append( nodeinfo_onpath_to_xmlelement( nodeinfo ) )
    
    # mmh im not convinced
    return ET.tostring( elemroot, encoding=encoding_dict[ decode ] ).decode( \
                                                                        decode )

encoding_dict = {\
        "utf-8":"utf8",\
        "utf8":"utf8",\
        }

def pathoto_xmlelement( path ):
    elempath = ET.Element( xml_config.findpath )
    for i in range(len(path)):
        edge = path[i]
        tmpelem = ET.SubElement( elempath, xml_config.findpath_edge )
        tmpelem.set( xml_config.findpath_edge_index, str(i) )
        tmpelem.set( xml_config.findpath_edge_first, str(edge[0]) )
        tmpelem.set( xml_config.findpath_edge_second, str(edge[1]) )
        tmpelem.set( xml_config.findpath_edge_third, str(edge[2]) )
        tmpelem.set( xml_config.findpath_edge_fourth, str(edge[3]) )
        
    return elempath

def nodeinfo_onpath_to_xmlelement( nodeinfo ):
    elemnodeinfo = ET.Element( xml_config.nodeinfo_onpath )
    for i in range(len(nodeinfo)):
        tmpinfo = nodeinfo[i]

        tmpelem = ET.SubElement( elemnodeinfo, xml_config.nodeinfo_onpath_node )
        tmpelem.set( xml_config.nodeinfo_onpath_node_index, str(i) )
        tmpelem.set( xml_config.nodeinfo_onpath_node_first, str(tmpinfo[0]) )
        tmpelem.set( xml_config.nodeinfo_onpath_node_second, str(tmpinfo[1]) )
    return elemnodeinfo

def replace_nodenames_for_samenames( same_nodes, \
                                    translator, graph_old, graph_new ):
    nodes_old = graph_old.nodes()
    nodes_new = graph_new.nodes()
    same_nodes_translator = { x[0]:x[1] for x in same_nodes }
    replacement_in_new = {}
    replacement_in_old = {}
    for oldnode in translator:
        newname = translator.index( oldnode )
        if newname in nodes_old and newname not in replacement_in_old:
            replacement_in_old.update( { newname: "unique"+str(newname) } )
        if newname in nodes_new and newname not in replacement_in_new:
            replacement_in_new.update( { newname: "unique"+str(newname) } )
        replacement_in_old.update( { oldnode: newname } )
        if oldnode in same_nodes_translator:
            replacement_in_new.update(  \
                                    {same_nodes_translator[oldnode]: newname} )
    netx.relabel_nodes( graph_old, replacement_in_old, copy=False )
    netx.relabel_nodes( graph_new, replacement_in_new, copy=False )
    return graph_old, graph_new, replacement_in_old, replacement_in_new


find_startpoint_dictionary = {}

def possible_start_at():
    return list( find_startpoint_dictionary.keys() ) #use keys for readability

def _start_at_bottomleft_sortkey( node ):
    """
    :type node: tuple; len=2; type(tuple[i]) = int or float
    """
    return node[0] - math.exp( -1-node[1] )
def _start_at_bottomright_sortkey( node ):
    return node[0] + math.exp( -1-node[1] )
def _start_at_topleft_sortkey( node ):
    return -node[0] - math.exp( -1-node[1] )
def _start_at_topright_sortkey( node ):
    return -node[0] + math.exp( -1-node[1] )
def _start_at_bottomleft( graph ):
    mynodes = list( graph.nodes() )
    mynodes.sort( key=_start_at_bottomleft_sortkey )
    return mynodes[0]
def _start_at_bottomright( graph ):
    mynodes = list( graph.nodes() )
    mynodes.sort( key=_start_at_bottomright_sortkey )[0]
    return mynodes[0]
def _start_at_topleft( graph ):
    mynodes = list( graph.nodes() )
    mynodes.sort( key=_start_at_topleft_sortkey )[0]
    return mynodes[0]
def _start_at_topright( graph ):
    mynodes = list( graph.nodes() )
    mynodes.sort( key=_start_at_topright_sortkey )[0]
    return mynodes[0]
find_startpoint_dictionary.update( {\
        "bottomleft":_start_at_bottomleft, \
        "bottomright":_start_at_bottomright, \
        "topleft":_start_at_topleft, \
        "topright":_start_at_topright, \
        })

def _start_at_marked( graph ):
    """
    starting is saved in attribute 'mark' and should be 'startingpoint'
    removes mark
    """
    markdictionary = netx.get_node_attributes( graph, "mark" )
    foundnode = None
    for asd in markdictionary:
        if markdictionary[asd] == "startingpoint":
            extraoptions = graph.nodes( data=True )
            extraoptions[asd].pop("mark")
            extraoptions[asd]["stitchtype"] = \
                            extraoptions[asd].pop("alternative_stitchtype")
            return asd
find_startpoint_dictionary.update({ "marked":_start_at_marked })



def find_common_node( graph1, graph2, startnode_in1, startnode_in2 ):
    """
    :param startnode_in1: this is a node in graph1 which is the same node as 
                        staertnode_in2 in graph2
                        This is needed for a common starting point
    :type graph1: networkx.Graph
    :type graph2: networkx.Graph
    :type startnode_in1: hashable
    :type startnode_in2: hashable
    """
    common_nodes1 = [ startnode_in1 ]
    common_nodes2 = [ startnode_in2 ]
    i = 1
    tobevisited_queue = [ startnode_in1 ]
    while 0 < len( tobevisited_queue ):
        tmpnode = tobevisited_queue.pop(0)
        testedpairs = find_unambiguous_assignable_edges( tmpnode, \
                                                graph1, graph2,\
                                                common_nodes1, common_nodes2 )
        for (tmpedge1, tmpedge2) in testedpairs:
            tmpnodes1 = add_missing_node( common_nodes1, tmpedge1 )
            tmpnodes2 = add_missing_node( common_nodes2, tmpedge2 )
            #check if something was added
            if len(tmpnodes1) > len(common_nodes1):
                # check if subgraphs from corresponding nodes are congruent to
                # one another
                if graph1.subgraph( tmpnodes1 ) == graph2.subgraph( tmpnodes2 ):
                    added_node = [x for x in tmpnodes1 \
                                    if x not in common_nodes1][0]
                    tobevisited_queue.append( added_node )
                    common_nodes1 = tmpnodes1
                    common_nodes2 = tmpnodes2

    return [ (common_nodes1[i], common_nodes2[i]) \
                for i in range(len(common_nodes1))]

def add_missing_node( nodelist, edge ):
    copy_nodelist = list( nodelist )
    for node in [ edge[0], edge[1] ]:
        if node not in nodelist:
            copy_nodelist.append( node )
    return copy_nodelist

def find_unambiguous_assignable_edges( tmpnode, \
                                        graph1, graph2, \
                                        common_nodes1, common_nodes2, \
                                        ):
    """
    returns a pair of two unambiguous assignable edges
    :rtype: list of tuples of edges
    """
    neighbours1 = graph1.edges( tmpnode, data=True )
    neighbours1 = [ x for x in neighbours1 if x[0] not in common_nodes1 ] \
                + [ x for x in neighbours1 if x[1] not in common_nodes1 ]
    sim_dict1 = order_similar_edges( graph1, neighbours1 )
    similar_tmpnode = common_nodes2[ common_nodes1.index(tmpnode) ]
    neighbours2 = graph2.edges( similar_tmpnode, data=True )
    neighbours2 = [ x for x in neighbours2 if x[0] not in common_nodes2 ] \
                + [ x for x in neighbours2 if x[1] not in common_nodes2 ]
    sim_dict2 = order_similar_edges( graph2, neighbours2 )
    simpair = []
    for key in sim_dict1:
        try:
            list1 = sim_dict1[key]
            list2 = sim_dict2[key]
            if len(list1) == 1 and len(list2) == 1:
                simpair.append( (list1[0], list2[0]) )
        except KeyError:
            pass
    return simpair

def order_similar( graph ):
    """
    :todo: not used anymore
    """
    edges = graph.edges( data=True )
    return order_similar_edges( graph, edges )


def order_similar_edges( graph, edges ):
    tmp_edgelist = None
    similar_dict = {}
    for edge in edges:
        tmp_edgelist = similar_dict.setdefault( edgetohash( graph,edge), list())
        tmp_edgelist.append( edge )
    return similar_dict
        


def edgetohash( graph, edge ):
    """
    return hashable which is not bound to the identification of the edge 
    or nodes. Only values the extra data on the edge and the nodes.
    """
    if isinstance( edge[-1], dict ):
        info = edge[-1]
    else:
        info = graph.edges( edge, data=True )
    node1info = graph.nodes( data=True )[ edge[0] ]
    node2info = graph.nodes( data=True )[ edge[1] ]
    return tuple(\
            [ (x,node1info[x]) for x in node1info ]\
            +[ (x,info[x]) for x in info ]\
            +[ (x,node2info[x]) for x in node2info ]\
            )


def get_node_difference( same_nodes_pairs, all_nodes1, all_nodes2 ):
    tmpnodes1, tmpnodes2 = set(all_nodes1), set(all_nodes2)
    for pair in same_nodes_pairs:
        tmpnodes1.remove(pair[0])
        tmpnodes2.remove(pair[1])
    return tmpnodes1, tmpnodes2

def generate_replacement_from_graphs( graph_old, graph_new, nodes=None ):
    """
    :todo: add exception controlment when networkx.is_connected supports
            directed Graphs
    """
    same_nodes = find_common_node( graph_old, graph_new, "start", "start" )
    difference_nodes_old, difference_nodes_new = \
            get_node_difference( same_nodes, graph_old.nodes(), \
                                graph_new.nodes())
    nodes_subgraph_old = get_neighbours_from( graph_old, difference_nodes_old )
    nodes_subgraph_old.update( difference_nodes_old )
    nodes_subgraph_new = get_neighbours_from( graph_new, difference_nodes_new )
    nodes_subgraph_new.update( difference_nodes_new )

    # currently netx.is_connected doesnt support directed graphs
    #old_is_connected = netx.is_connected( \
    #                    graph_old.subgraph( nodes_subgraph_old ))
    #new_is_connected = netx.is_connected( \
    #                    graph_new.subgraph( nodes_subgraph_new ))
    #if not( old_is_connected and new_is_connected ):
    #    raise manualtoverbesserung_Exception( \
    #                        "subgraphs, that differentiate are not connected",\
    #                        "old graph is connected: %s,"%( old_is_connected)\
    #                        + "new graph is connected: %s"%( new_is_connected))
    # currently netx.is_connected doesnt support directed graphs

    return nodes_subgraph_old, nodes_subgraph_new, same_nodes
