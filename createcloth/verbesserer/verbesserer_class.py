from ..strickgraph.fromknitmanual import frommanual
from ..strickgraph.strickgraph_base import get_neighbours_from, strickgraph, stricksubgraph

import networkx as netx
import math
from ..strickgraph.strickgraph_replacesubgraph import create_pathforhashing, follow_cached_path
from . import xml_config
import xml.etree.ElementTree as ET
from .manualtoverbesserung import generate_replacement_from_graphs, find_startpoint_dictionary, replace_nodenames_for_samenames, replace_nodes_in_list, build_xmlElement
import copy
import io
from extrasfornetworkx import generate_verbesserer_from_graph_difference
import extrasfornetworkx

class FindError( Exception ):
    pass

class verbesserer():
    """
    :todo: implement startpoint as getter and setter so the findgraph is
            automaticly searched
            try to initialise with only the subgraphs
    """
    def __init__( self, oldgraph, newgraph, oldgraph_nodes, \
                    newgraph_nodes, startpoint, oldgraph_identificationpath, \
                    oldgraph_nodeinfoonpath, \
                    nodeattributes=["stitchtype", "side"], \
                    edgeattributes=["edgetype"] ):
        self.oldgraph = oldgraph
        self.newgraph = newgraph
        self.oldgraph_nodes = oldgraph_nodes
        self.newgraph_nodes = newgraph_nodes
        self.startpoint = startpoint
        self.oldgraph_identificationpath = oldgraph_identificationpath
        self.oldgraph_nodeinfoonpath = oldgraph_nodeinfoonpath

    def __eq__( self, other ):
        """
        :todo: add starting_point to verification process
        """
        if not isinstance( other, type(self) ):
            return False
        a = self.oldgraph.subgraph( self.oldgraph_nodes ) \
                == other.oldgraph.subgraph( other.oldgraph_nodes )
        b = self.newgraph.subgraph( self.newgraph_nodes ) \
                == other.newgraph.subgraph( other.newgraph_nodes )
        #c = self.startpoint == other.startpoint #this doesnt work
        #because the identifier of the startpoint could be different
        return a and b

    def replace_in_graph( self, graph, startnode ):
        # find subgraph to replace
        try:
            foundsubgraph, foundtranslator = _replace_findsubgraph_in_original(\
                graph, startnode, \
                self.oldgraph_identificationpath, self.oldgraph_nodeinfoonpath,\
                self.oldgraph.subgraph( self.oldgraph_nodes ))
        except KeyError as err:
            print( err.args )
            raise err
            return False

        uniquetranslator = tounique_translator( graph.nodes(), \
                                                list(self.oldgraph.nodes()) \
                                                + list(self.newgraph.nodes()) )
        uniquetranslator.update( foundtranslator )

        oldgraph, oldgraph_nodes, newgraph, newgraph_nodes =\
                    _create_update_graphs( self.oldgraph, self.oldgraph_nodes,\
                                            self.newgraph, self.newgraph_nodes,\
                                            uniquetranslator )

        nodes_to_remove = set(oldgraph_nodes).difference(newgraph_nodes)
        remove_edges = oldgraph.subgraph(oldgraph_nodes ).edges()
        graph.remove_edges_from( remove_edges )
        graph.remove_nodes_from( nodes_to_remove )
        graph.update( newgraph.subgraph( newgraph_nodes ) )
        return True

def _create_update_graphs( oldgraph, oldgraph_nodes, newgraph, newgraph_nodes, \
                                translator):
        tmpoldgraph, tmpoldgraph_nodes = copy.deepcopy((oldgraph, \
                                                        oldgraph_nodes))
        tmpnewgraph, tmpnewgraph_nodes = copy.deepcopy((newgraph, \
                                                        newgraph_nodes))

        tmplist = []
        for x in tmpoldgraph_nodes:
            if x in translator:
                tmplist.append( translator[x] )
            else:
                tmplist.append( x )
        tmpoldgraph_nodes = tmplist
        tmplist = []
        for x in tmpnewgraph_nodes:
            if x in translator:
                tmplist.append( translator[x] )
            else:
                tmplist.append( x )
        tmpnewgraph_nodes = tmplist
        tmplist = None
        tmpoldgraph = netx.relabel_nodes( tmpoldgraph, translator )
        tmpnewgraph = netx.relabel_nodes( tmpnewgraph, translator )
        return tmpoldgraph, tmpoldgraph_nodes, tmpnewgraph, tmpnewgraph_nodes

def _replace_findsubgraph_in_original(graph, startnode, identificationpath, \
                    nodeinfoonpath, target_subgraph):
        foundsubgraph = None
        foundtranslator = None
        nodesets = follow_cached_path( \
                                            graph, startnode, \
                                            identificationpath,\
                                            nodeinfoonpath,\
                                        )
        if len(nodesets) == 0:
            args = [ graph.nodes( data=True )[startnode], \
                    nodeinfoonpath ]
            raise FindError( *args )
        for nodes, translator in nodesets:
            tmpsubgraph = graph.subgraph( nodes )
            if tmpsubgraph == target_subgraph:
                return tmpsubgraph, translator
        raise FindError("didnt found graph here", \
                            graph.nodes( data=True )[startnode], \
                            nodeinfoonpath, nodesets)


def tounique_translator( staticnodes, transnodes ):
    translator = dict()
    union = set(staticnodes).union(transnodes)
    i=0
    for x in transnodes:
        if x in staticnodes:
            while i in union or str(i) in union:
                i = i+1
            translator.update({ x:str(i) })

            i = i+1
    return translator



def verbesserungtoxml( verbesserer ):
    subgraph_old = verbesserer.oldgraph.subgraph( verbesserer.oldgraph_nodes )
    subgraph_new = verbesserer.newgraph.subgraph( verbesserer.newgraph_nodes )
    path = verbesserer.oldgraph_identificationpath
    nodeinfo = verbesserer.oldgraph_nodeinfoonpath
    return build_xmlElement( subgraph_old, subgraph_new, path, nodeinfo )

def verbessererfromxml( xml, mynamespace='' ):
    """
    :type xml: str
    :todo: think about stream support
    """
    ET.register_namespace( "graphverbesserer", xml_config.namespace )
    ET.register_namespace( "grml", "http://graphml.graphdrawing.org/xmlns" )
    ET.register_namespace( "xsi", "http://www.w3.org/2001/XMLSchema-instance" )

    xml_str = tostringinterpreter( xml )

    verbesserer_xml = ET.fromstring( xml_str )
    #print( ET.tostring( verbesserer_xml ).decode("utf8"))
    #oldgraphml_iter = verbesserer_xml.findall( mynamespace + xml_config.oldgraph )
    oldgraphml_container = verbesserer_xml.find( xml_config.oldgraph )
    oldgraphml = list( oldgraphml_container )[0]
    oldgraphml_str = ET.tostring( oldgraphml ).decode("utf-8")
    #mystrick_old = strickgraph( netx.parse_graphml( oldgraphml_str, \
    mystrick_old = stricksubgraph( netx.parse_graphml( oldgraphml_str, \
                                                    force_multigraph=True ))

    newgraphml_container = verbesserer_xml.find( xml_config.newgraph )
    newgraphml = list( newgraphml_container )[0]
    newgraphml_str = ET.tostring( newgraphml ).decode("utf-8")
    #mystrick_new = strickgraph( netx.parse_graphml( newgraphml_str, \
    mystrick_new = stricksubgraph( netx.parse_graphml( newgraphml_str, \
                                                    force_multigraph=True ))

    path_container = verbesserer_xml.find( xml_config.findpath )
    path = pathfrom_xmlelement( path_container )
    nodeinfo_container = verbesserer_xml.find( xml_config.nodeinfo_onpath )
    nodeinfo = nodeinfo_from_xmlelement( nodeinfo_container )
    
    return verbesserer( mystrick_old, mystrick_new, \
                        mystrick_old.nodes(), mystrick_new.nodes(), \
                        '0', path, nodeinfo )


def tostringinterpreter( myobject ):
    return tostringinterpreter_dict[type(myobject)]( myobject )


tostringinterpreter_dict = {}
def strtostr( mystr ):
    return mystr
tostringinterpreter_dict.update({ str: strtostr })

def bufferedreadertostr( mybufferedreader ):
    """
    :todo: why must i add '>' ???
    """
    mystring = [ x[:-1].decode("utf-8") for x in mybufferedreader ]
    mystring = "\n".join(mystring) + ">"
    return mystring
tostringinterpreter_dict.update({ io.BufferedReader: bufferedreadertostr })
    

def nodeinfo_from_xmlelement( xmlelement ):
    subelements = xmlelement.findall( xml_config.nodeinfo_onpath_node )
    nodeinfo = list( range( len(subelements)))  # generate list of 
                                                # length(subelements)
    for subelem in subelements:
        index = subelem.attrib[ xml_config.nodeinfo_onpath_node_index ]
        nodeinfo[ int(index) ] = ( \
                        subelem.attrib[xml_config.nodeinfo_onpath_node_first],\
                        subelem.attrib[xml_config.nodeinfo_onpath_node_second],\
                        )
    return nodeinfo

def pathfrom_xmlelement( xmlelement ):
    subelements = xmlelement.findall( xml_config.findpath_edge )
    path = list( range( len(subelements))) #generate list of length(subelements)
    for subelem in subelements:
        index = subelem.attrib[xml_config.findpath_edge_index ]
        path[ int(index) ] = ( \
                subelem.attrib[ xml_config.findpath_edge_first ],\
                subelem.attrib[ xml_config.findpath_edge_second ],\
                subelem.attrib[ xml_config.findpath_edge_third ],\
                subelem.attrib[ xml_config.findpath_edge_fourth ],\
                )
    return path


def manualtoersetzer( manual_old, manual_new, start_at="bottomleft", \
                                manual_type="machine", startside="right",\
                                startpoint_method="marked", reversed=False):
    """
    generates everything i need for replacing a subgraph
    :param startpoint_method: keyword for finding the startpoint for 
                                replacement
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

            Also remove unneeded node and edge information
            currently only mark information is removed and this only works 
            via extra if function. This has to be optimised somehow
    """
    old_graph = frommanual( manual_old, manual_type=manual_type, \
                                    startside=startside,reversed=reversed )
    new_graph = frommanual( manual_new, manual_type=manual_type, \
                                    startside=startside, reversed=reversed )


    startold, startnew = findstartnode_dict[ startpoint_method ](\
                                                old_graph, new_graph )
    if startpoint_method == "marked":
        newstitchtypes = netx.get_node_attributes(old_graph, \
                                                    "alternative_stitchtype" )
        netx.set_node_attributes( old_graph, newstitchtypes, "stitchtype" )
        newstitchtypes = netx.get_node_attributes(new_graph, \
                                                    "alternative_stitchtype" )
        netx.set_node_attributes( new_graph, newstitchtypes, "stitchtype" )


    #old_graph, startold, map_old = nodestosimplenames( old_graph, startold )
    #new_graph, startnew, map_new = nodestosimplenames( new_graph, startnew )
    try:
        returnv= extrasfornetworkx.generate_verbesserer_from_graph_difference(
                                            old_graph, new_graph,\
                                            startold,\
                                            startnew,\
                                            "edgetype", ["stitchtype", "side"] )
    except KeyError as err:
        if err.args[0] in [ "start", "end" ]:
            err.args = ( *err.args, "Most likely the oldgraph and newgraph "\
                            + "are not similar or the startpoint is not "\
                            + "chosen as a similar point",\
                            "the detection of similar graphnodes is still not fully functionable")
        raise err
    return returnv



    generate_verbesserer_from_graph_difference( \
                                            old_graph, new_graph, \
                                            startold, startnew, \
                                            "edgetype", ["stitchtype", "side"] )
    nodes_subgraph_old, nodes_subgraph_new, same_nodes = \
                                        generate_replacement_from_graphs( \
                                                    old_graph, new_graph )

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
    #subgraph_old = old_graph.subgraph( nodes_subgraph_old )
    #subgraph_new = new_graph.subgraph( nodes_subgraph_new )

    return verbesserer( old_graph, new_graph, \
                        nodes_subgraph_old, nodes_subgraph_new, \
                        starting_point, path, nodeinfo )

def nodestosimplenames( graph, startnode ):
    mynodes = [ node for node in graph.nodes() if node not in ["start", "end"]]
    mymap = { mynodes[i]:i for i in range(len(mynodes)) }
    backmap = { mymap[node]:node for node in mymap }
    newgraph = netx.relabel_nodes( graph, mymap )
    return newgraph, mymap[startnode], backmap

def findstartnode_marked( oldgraph, newgraph ):
    old_nodeattr = netx.get_node_attributes( oldgraph, "mark" )
    new_nodeattr = netx.get_node_attributes( newgraph, "mark" )
    startingpoint_old_list = [ x for x in old_nodeattr \
                                if old_nodeattr[x] == "startingpoint"]
    startingpoint_new_list = [ x for x in new_nodeattr \
                                if new_nodeattr[x] == "startingpoint"]
    try:
        old_startingpoint = startingpoint_old_list[0]
    except IndexError as err:
        err.args = ( *err.args, "findmethod for graphreplacement is chosen"\
                    +"marked but no 'marked' node with attribute"\
                    +"'startingpoint' was given", "happened in the old Graph")
        raise err
    try:
        new_startingpoint = startingpoint_new_list[0]
    except IndexError as err:
        err.args = ( *err.args, "findmethod for graphreplacement is chosen"\
                    +"marked but no 'marked' node with attribute"\
                    +"'startingpoint' was given", "happened in the old Graph")
        raise err
    return old_startingpoint, new_startingpoint

findstartnode_dict = {\
        "marked": findstartnode_marked, \
        }

def frommanual_without_startandend( manual_new, manual_type=None, \
                                startside=None ):
    """
    obsolete
    :todo: this function may be obsolete because the node start and end should
    not be in the subgraph that will be replaced
    """
    graph = frommanual( manual_new, manual_type=manual_type, \
                                                        startside=startside )
    #graph_nodes = set( graph).difference([ "start", "end" ])
    graph_nodes = set( graph).difference([])
    subgraph = graph.subgraph( graph_nodes )
    return subgraph
