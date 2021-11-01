from .verbesserer_class import FindError
import xml.etree.ElementTree as ET
import logging
import extrasfornetworkx as efn
import networkx as netx
import itertools as it
import math
from .. import helper_limitcalculationtime as timelimiter
logger = logging.getLogger( __name__ )

XML_SIDEALTERATOR_NAME = "sidealterator"


class SkipGeneration( Exception ):
    pass

class sidealterator():
    """Alterator to alterate bth sides at the same time. Giuven a line number
    the alterator will look if it can alterate given strickgraph at this line
    Strickgraphs are not limitied to maximal size. There should be a limit of
    minimal width
    :todo: minimal width
    :todo: replace_in_graph, fromxml, toxml
    :ivar alterator_left:
    :ivar leftstartindex:
    :ivar alterator_right:
    :ivar rightstartindex:
    """
    def __init__( self, alterator_left, leftstartindex:int, \
                        alterator_right, rightstartindex:int ):
        assert type(leftstartindex)==int, "wrong type"
        assert type(rightstartindex)==int, "wrong type"
        self.alterator_left = alterator_left
        self.leftstartindex = leftstartindex
        self.alterator_right = alterator_right
        self.rightstartindex = rightstartindex

    def replace_in_graph( self, strickgraph, linenumber, row=None, nodeattributes=None, edgeswithlabel=None ):
        """mainmethod replkaces in graph at given line

        :raises: FindError
        :param row: use this to accelerate this method
        """
        if row == None:
            row = strickgraph.get_rows()[ linenumber ]
        startnodeleft = row[ self.leftstartindex ]
        startnoderight = row[ self.rightstartindex ]
        if nodeattributes is None:
            nodeattributes = graph.get_nodeattributes()
        if edgeswithlabel is None:
            edgeswithlabel = graph.get_edges_with_labels()

        logger.debug( "checking if graph ist replaceable" )
        cond1 = self.alterator_left.isreplaceable( strickgraph, startnodeleft, nodeattributes=nodeattributes, edgeswithlabel=edgeswithlabel )
        if not cond1:
            raise FindError()
        cond2 = self.alterator_right.isreplaceable( strickgraph,startnoderight, nodeattributes=nodeattributes, edgeswithlabel=edgeswithlabel )
        if not cond2:
            raise FindError()
        logger.info( "replaceleft" )
        strickgraph = self.alterator_left.replace_in_graph( strickgraph, startnodeleft )
        logger.info( "replaceright" )
        strickgraph = self.alterator_right.replace_in_graph( strickgraph, startnoderight )
        return strickgraph

    @classmethod
    def from_linetypes( cls, linetype_out, linetype_in, upedges_out, \
                            upedges_in, changedline_id, skip_if_in_list=None ):
        """
        :type linetype_out: List[ createcloth.plainknit.state ]
        :type linetype_in: List[ createcloth.plainknit.state ]
        :type upedges_out: List[ int ]
        :type upedges_in: List[ int ]
        :type changedline_id: int
        :raises: SkipGeneration
        """
        great_graph = create_graph_from_linetypes( linetype_in, upedges_in )
        if skip_if_in_list is not None:
            for i in skip_if_in_list:
                try:
                    tmp_graph = create_graph_from_linetypes( linetype_out, upedges_out)
                    tmp_graph = i.replace_in_graph( tmp_graph, changedline_id )
                    if tmp_graph == great_graph:
                        raise SkipGeneration()
                    raise Exception( "This should never trigger" )
                except FindError:
                    continue
        less_graph = create_graph_from_linetypes( linetype_out, upedges_out)

        if linetype_out[0] == linetype_in[1]:
            startnode = (0,0)
        else:
            startnode = (len( linetype_out )-1, 0)

        return cls.from_graphdifference( less_graph, great_graph, startnode, changedline_id )
    
    @classmethod
    def from_xml( cls, xmlstring ):
        """from given xmlstring"""
        from extrasfornetworkx import xml_config
        ET.register_namespace( "asd", xml_config.namespace )
        ET.register_namespace( "grml", xml_config.namespace_graphml )
        ET.register_namespace( "xsi", xml_config.namespace_xsi )

        verbesserer_xml = ET.fromstring( xmlstring )
        try:
            return cls.from_xmlobject( verbesserer_xml )
        except Exception as err:
            raise Exception(xmlstring) from err
    @classmethod
    def from_xmlobject( cls, xml_elem ):
        """
        :raises: Exception
        :todo: raise custom exceptions
        """
        from ..verbesserer.verbesserer_class import strickalterator
        from extrasfornetworkx import xml_config
        ET.register_namespace( "asd", xml_config.namespace )
        ET.register_namespace( "grml", xml_config.namespace_graphml )
        ET.register_namespace( "xsi", xml_config.namespace_xsi )

        full_name = "{%s}%s" %( xml_config.namespace, XML_SIDEALTERATOR_NAME )
        assert full_name == xml_elem.tag, f"wrong elementtype, need {full_name}"
        subelements = list( xml_elem )
        rightindex, leftindex= None, None
        rightverbesserer, leftverbesserer = None, None
        for el in subelements:
            if el.attrib["side"] == "right":
                if rightindex is not None:
                    raise Exception("doubled rightelement")
                rightindex = int( el.attrib["index"] )
                rightverbesserer = strickalterator.from_xmlobject( el )
            elif el.attrib["side"] == "left":
                if leftindex is not None:
                    raise Exception("doubled rightelement")
                leftindex = int( el.attrib["index"] )
                leftverbesserer = strickalterator.from_xmlobject( el )
            else:
                raise Exception( "element without sidefound" )
        if not all((leftverbesserer, leftindex, rightverbesserer, rightindex)):
            raise Exception( "not all info found" )
        return cls( leftverbesserer, leftindex, rightverbesserer, rightindex )


    def to_xml( self, encoding ="utf-8" ):
        """to xmlstring

        :param encoding: same as xml.etree.ElementTree.tostring
        :type encoding: str
        """
        from extrasfornetworkx import xml_config
        ET.register_namespace( "asd", xml_config.namespace )
        ET.register_namespace( "grml", xml_config.namespace_graphml )
        ET.register_namespace( "xsi", xml_config.namespace_xsi )
        elemroot = self.toxmlelem()
        xmlbytes = ET.tostring( elemroot, encoding=encoding )
        xmlstring = xmlbytes.decode( encoding )
        return xmlstring

    def toxmlelem( self ):
        """to xml element

        :rtype: xml.etree.ElementTree.Element
        """
        from extrasfornetworkx import xml_config
        ET.register_namespace( "asd", xml_config.namespace )
        ET.register_namespace( "grml", xml_config.namespace_graphml )
        ET.register_namespace( "xsi", xml_config.namespace_xsi )

        full_name = "{%s}%s" %( xml_config.namespace, XML_SIDEALTERATOR_NAME )
        elemroot = ET.Element( full_name )
        elemroot.append( self.alterator_left.toxmlelem() )
        elemroot[-1].attrib["side"] = "left"
        elemroot[-1].attrib["index"] = str(self.leftstartindex)
        elemroot.append( self.alterator_right.toxmlelem() )
        elemroot[-1].attrib["side"] = "right"
        elemroot[-1].attrib["index"] = str(self.rightstartindex)
        return elemroot


    @classmethod
    def from_graphdifference( cls, source_strickgraph, target_strickgraph, \
                                            startnode, changedline_id):
        """Uses twographs with alterated line

        :param startnode: Startnode to have a shared node for graphdifference
        :todo: remove use of startnode
        """
        logger.info( f"create {cls} from graphdifference" )
        replacement_graph1, replacement_graph2, translator \
                                = twographs_to_replacement( \
                                source_strickgraph, target_strickgraph, \
                                startnode, changedline_id )
        translator = { a:b for a, b in translator }
        difference_graph1 =set(replacement_graph1).difference(translator.keys())
        difference_graph2 =set(replacement_graph2).difference(translator.values())
        logger.debug( f"difference input: {difference_graph1}" )
        logger.debug( f"difference output: {difference_graph2}" )
        leftnodes1, leftnodes2, startnode1_left, leftindex, \
                rightnodes1, rightnodes2, startnode1_right, rightindex \
                = separate_wholegraphs_to_leftright_insulas( \
                        difference_graph1, difference_graph2, translator, \
                        source_strickgraph, target_strickgraph, changedline_id )
        mykey = lambda x: x if type(x)==tuple \
                        else (x,) if type(x)==int \
                        else (0,)
        logger.debug( f"startnodes l/r: {startnode1_right}, {startnode1_left}" )
        logger.debug( "leftnodes1: (l:%i) %s" %( len(leftnodes1), sorted(leftnodes1, key=mykey) ))
        logger.debug( "leftnodes2: (l:%i) %s" %( len(leftnodes2), sorted(leftnodes2, key=mykey) ))
        logger.debug( "rightnodes1: (l:%i) %s" %( len(rightnodes1), sorted(rightnodes1, key=mykey) ))
        logger.debug( "rightnodes2: (l:%i) %s" %( len(rightnodes2), sorted(rightnodes2, key=mykey) ))

        logger.info("create left alterator")
        #startnode2_left = translator[ startnode1_left ]
        lefttrans = { a:b for a, b in translator.items() if a in leftnodes1 }
        logger.debug( f"nodes1: {leftnodes1}")
        logger.debug( f"nodes2: {leftnodes2}")
        a = generate_verbesserer_asdf( \
                                source_strickgraph, target_strickgraph, \
                                leftnodes1, leftnodes2, \
                                startnode1_left,
                                lefttrans )
        tmp_bordernodes1 = get_innerborder( leftnodes1, source_strickgraph )
        tmp_bordernodes2 = get_innerborder( leftnodes2, target_strickgraph )
        oldtrans = { y:x for x,y in a.logging_information['translator oldgraph'].items()}
        newtrans = { y:x for x,y in a.logging_information['translator newgraph'].items()}
        orig_nodes_to_remove = [oldtrans[n] for n in a.nodes_to_remove()]
        orig_nodes_to_add = [newtrans[n] for n in a.nodes_to_add()]
        outsorted_oldnodes=set(orig_nodes_to_remove).intersection(tmp_bordernodes1)
        outsorted_newnodes =set(orig_nodes_to_add).intersection(tmp_bordernodes2)
        assert set() == outsorted_oldnodes == outsorted_newnodes, \
                "lefttrans problem, bordernodes, cant be added or removed: "\
                f"removed oldbordernodes: {outsorted_oldnodes} added "\
                f"newbordernodes: {outsorted_newnodes}"
        logger.info("create right alterator")
        #startnode2_right = translator[ startnode1_right ]
        righttrans = { a:b for a, b in translator.items() if a in rightnodes1 }
        logger.debug( f"nodes1: {rightnodes1}")
        logger.debug( f"nodes2: {rightnodes2}")
        b = generate_verbesserer_asdf( \
                                source_strickgraph, target_strickgraph, \
                                rightnodes1, rightnodes2, \
                                startnode1_right, \
                                righttrans )
        tmp_bordernodes1 = get_innerborder( rightnodes1, source_strickgraph )
        tmp_bordernodes2 = get_innerborder( rightnodes2, target_strickgraph )
        oldtrans = { y:x for x,y in b.logging_information['translator oldgraph'].items()}
        newtrans = { y:x for x,y in b.logging_information['translator newgraph'].items()}
        orig_nodes_to_remove = [oldtrans[n] for n in b.nodes_to_remove()]
        orig_nodes_to_add = [newtrans[n] for n in b.nodes_to_add()]
        outsorted_oldnodes=set(orig_nodes_to_remove).intersection(tmp_bordernodes1)
        outsorted_newnodes =set(orig_nodes_to_add).intersection(tmp_bordernodes2)
        assert set() == outsorted_oldnodes == outsorted_newnodes, \
                "righttrans problem, bordernodes, cant be added or removed: "\
                f"removed oldbordernodes: {outsorted_oldnodes} added "\
                f"newbordernodes: {outsorted_newnodes}"

        return cls( a, leftindex, b, rightindex )

def generate_verbesserer_asdf( graph1, graph2, \
                                subnodelist1, subnodelist2, \
                                startnode1, starttranslation ):
    subgraph1 = graph1.subgraph( subnodelist1 )
    subgraph2 = graph2.subgraph( subnodelist2 )
    nodelabels1 = subgraph1.get_nodeattributes()
    edgelabels1 = subgraph1.get_edges_with_labels()
    nodelabels2 = subgraph2.get_nodeattributes()
    edgelabels2 = subgraph2.get_edges_with_labels()
    from ..verbesserer.verbesserer_class import strickalterator
    logger.debug("input for strickgraphalterator: %s, %s, %s, %s, %s " \
            % (nodelabels1, edgelabels1, nodelabels2, edgelabels2, \
            starttranslation ) )
    return strickalterator.from_graph_difference(
                                        nodelabels1, edgelabels1,\
                                        nodelabels2, edgelabels2, \
                                        startnode1, \
                                        starttranslation )

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
    translation = { nodetrans1[v1]: nodetrans2[v2] \
                        for v1, v2 in starttranslation.items() }

    from ..verbesserer.verbesserer_class import strickalterator
    return strickalterator.from_graph_difference(
                                        nodelabels1, edgelabels1,\
                                        nodelabels2, edgelabels2, \
                                        nodetrans1[startnode1], \
                                        #nodetrans2[startnode2], \
                                        translation )


from ..strickgraph import strickgraph
from ..stitchinfo import basic_stitchdata as glstinfo
def create_graph_from_linetypes( linetypes, upedges, startside="right" ):
    sides = ("right", "left") if startside=="right" else ("left", "right")
    downedges = [ None, *upedges ]
    upedges = [ *upedges, None ]
    iline = range(len(downedges))
    allinfo = zip( linetypes, downedges, upedges, iline )
    try:
        graph_man = [ s.create_example_row( down, up, side=sides[i%2] ) \
                                for s, down, up, i in allinfo ]
    except Exception as err:
        raise Exception( [str(a) for a in linetypes], downedges, upedges, iline ) from err
        raise err
    graph = strickgraph.from_manual( graph_man, glstinfo, manual_type="machine")
    return graph


def inv( mydictionary ):
    assert type(mydictionary)==dict, "wrong use"
    return { b:a for a,b in mydictionary.items() }

def separate_wholegraphs_to_leftright_insulas( \
                        difference_graph1, difference_graph2, translator, \
                        less_graph, great_graph, changedline_id ):
    """

    :raises: NoLeftRightFound
    """
    linenodes_graph1 = [ node for node in less_graph.get_rows()[0] \
                        if node in difference_graph1 ]
    #half the graph
    rows = less_graph.get_rows()
    rowlength = sum( len(row) for row in rows ) / len(rows)
    isonleftside = lambda node: node[1] < rowlength
    less_graph_nodes = less_graph.get_nodes()
    great_graph_nodes = great_graph.get_nodes()

    #find left and right side to replace with insulas
    connected_insulas = less_graph.get_connected_nodes( difference_graph1 )
    connected_insulas2 = great_graph.get_connected_nodes( difference_graph2 )

    leftside_indices, rightside_indices \
                        = less_graph.get_sidemargins_indices()
    changed_row = rows[ changedline_id ]
    left_index = leftside_indices[ changedline_id ]
    right_index = rightside_indices[ changedline_id ]
    leftside_nodes = list(zip( changed_row[:left_index], range(left_index), ))
    rightside_nodes= list(zip( changed_row[right_index:],range(right_index,0),))
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

    mykey = lambda x: x if type(x)==tuple \
                        else (x,) if type(x)==int \
                        else (0,)
    qs = lambda x: sorted(x, key=mykey)


    neighbours1 = {}
    for v1, v2, label in less_graph.get_edges_with_labels():
        neighbours1.setdefault( v1, list() ).append( v2 )
        neighbours1.setdefault( v2, list() ).append( v1 )
    neighbours2 = {}
    for v1, v2, label in great_graph.get_edges_with_labels():
        neighbours2.setdefault( v1, list() ).append( v2 )
        neighbours2.setdefault( v2, list() ).append( v1 )
    try:
        uncommon_nodepairs1, uncommon_nodepairs2 \
                    = divide_into_two_parts( connected_insulas, neighbours1, \
                                            connected_insulas2, neighbours2,\
                                            translator )
    except IndexError as err:
        raise Exception( "couldnt find two distincly different nodeparts in "\
                            "differences. Most likely the difference nodes "\
                            "are to close to oneanother" ) from err
    logger.debug(" side-associated unccommonnodes:\nfirst: "\
            f"{uncommon_nodepairs1}\n second: {uncommon_nodepairs2}")
    
    lessgraphsplitter = split_graph_per_insula_in_nearestparts( 
                            [ uncommon_nodepairs1[0], uncommon_nodepairs2[0] ],\
                            less_graph )
    i = -1
    for asdf, qwer in ( uncommon_nodepairs1, uncommon_nodepairs2 ):
        i += 1
        nearnodes = less_graph.get_nodes_near_nodes( asdf )
        nearnodes = [ n for n in nearnodes \
                        if lessgraphsplitter[ n ] == i ]
        nearnodes = [ n for n in lessgraphsplitter \
                        if lessgraphsplitter[ n ] == i ]
        try:
            startnode1_left, leftindex \
                = ( (node, index) for node, index in leftside_nodes\
                if node in nearnodes ).__next__()
            leftnodes1 = set(nearnodes).union( asdf )
            leftnodes2 = set([translator[n] for n in nearnodes \
                                if n in translator]).union( qwer )
            continue
        except StopIteration:
            pass
        try:
            startnode1_right, rightindex \
                = ( (node, index) for node, index in rightside_nodes \
                if node in nearnodes ).__next__()
            rightnodes1 = set(nearnodes).union( asdf )
            rightnodes2 = set([translator[n] for n in nearnodes \
                                if n in translator ]).union( qwer )
        except StopIteration:
            pass
    try:
        return leftnodes1, leftnodes2, startnode1_left, leftindex, \
                rightnodes1, rightnodes2, startnode1_right, rightindex
    except NameError as err:
        raise NoLeftRightFound() from err

def divide_into_two_parts( connected_insulas1, neighbours1, \
                                            connected_insulas2, neighbours2,\
                                            samenode_translator ):
    """Divide nodes and uncommon nodes to blublub
    """
    all_nodes = tuple( it.chain( neighbours1.keys(), neighbours2.keys() ) )
    def nextname_gen():
        for i in range( len(all_nodes) ):
            if i not in neighbours1.keys():
                yield i
    translator = { a:i for a,i in zip(neighbours2, nextname_gen()) }
    translator.update(  { v2: v1 for v1, v2 in samenode_translator.items() } )
    antitrans = { v1: v2 for v2, v1 in translator.items() }
    trans_neighbours2 = {translator[n]: [ translator[q] for q in neighbourlist]\
                                    for n, neighbourlist in neighbours2.items()}
    trans_connected_insulas2 = [ tuple( translator[n] for n in insula) \
                                    for insula in connected_insulas2 ]

    metagraph = DistanceCalculationGraph()
    for v1, neighlist in neighbours1.items():
        for v2 in neighlist:
            metagraph.add_edge( v1, v2 )
    for v1, neighlist in trans_neighbours2.items():
        for v2 in neighlist:
            metagraph.add_edge( v1, v2 )

    insulagraph = netx.Graph()
    for i, ins1 in enumerate( connected_insulas1 ):
        insulagraph.add_node( (0,i), insulas=ins1 )
    for j, ins2 in enumerate( trans_connected_insulas2 ):
        insulagraph.add_node( (1,j), insulas=ins2 )
    for i, ins1 in enumerate( connected_insulas1 ):
        for j, ins2 in enumerate( trans_connected_insulas2 ):
            tmpdistance = metagraph.calc_distance( ins1, ins2 )
            insulagraph.add_edge( (0,i), (1,j), weight=max(0,tmpdistance-1) )
    distances = dict(netx.shortest_path_length( insulagraph, weight="weight" ))
    edges = list( (v1, v2, distances[v1][v2]) \
                    for v1, v2 in it.combinations(insulagraph.nodes(), 2) )
    edges.sort( key=lambda x: x[2] )

    for maxi in range( len(edges) ):
        mufugraph = netx.Graph()
        mufugraph.add_nodes_from( insulagraph.nodes( data=True ) )
        for i in range(maxi):
            mufugraph.add_edge( *edges[i][:2] )
        newinsulas = list( netx.connected_components( mufugraph ) )
        if len( newinsulas ) == 2:
            break
        elif len( newinsulas ) < 2:
            raise Exception( "couldnt find two distinct parts of the graph" )
    uncommon_nodespair1 = [ list(), list() ]
    for association, index in newinsulas[0]:
        nodelist = insulagraph.nodes[(association, index)]["insulas"]
        if association == 0:
            uncommon_nodespair1[ 0 ].extend( nodelist )
        else:
            uncommon_nodespair1[ 1 ].extend( \
                        ( antitrans.get( n, n ) for n in nodelist ) )
    uncommon_nodespair2 = [ list(), list() ]
    for association, index in newinsulas[1]:
        nodelist = insulagraph.nodes[(association, index)]["insulas"]
        if association == 0:
            uncommon_nodespair2[ 0 ].extend( nodelist )
        else:
            uncommon_nodespair2[ 1 ].extend( \
                        ( antitrans.get( n, n ) for n in nodelist ) )
    return uncommon_nodespair1, uncommon_nodespair2

class DistanceCalculationGraph( netx.Graph ):
    def calc_distance( self, nodelist1, nodelist2 ):
        nodelist1 = tuple(nodelist1)
        nodelist2 = tuple(nodelist2)

        calcgraph = netx.Graph( self )
        for v1, v2 in calcgraph.edges():
                tmpweight = 0 if v1 in nodelist1 and v2 in nodelist2 else 1
                calcgraph.edges[ v1, v2]["weight"] = tmpweight
        distances = dict( netx.shortest_path_length( calcgraph, weight="weight"))
        sourcenode = iter( nodelist1 ).__next__()
        d = math.inf
        for target in nodelist2:
            d = min( d, distances[sourcenode][target] )
        return d


def split_graph_per_insula_in_nearestparts( insulas, graph ):
    """This algorithm produces a split of a graph according to given 
    nodelist-insulas. So that every point of a split is nearest to its 
    corresponding insula. 
    if between two insulas there is a distance of only 1 node those 2 insulas
    will be combined

    :type insulas: List
    """
    import math
    neighbours = {}
    for v1, v2, label in graph.get_edges_with_labels():
        neighbours.setdefault( v1, list() ).append( v2 )
        neighbours.setdefault( v2, list() ).append( v1 )

    alliance = { n:(math.inf, -1) for n in neighbours.keys() }
    for i, nodes in enumerate( insulas ):
        assert len([ n for n in nodes if n not in neighbours.keys() ])==0, "asdf"
        graph = netx.Graph()
        for v1, v2list in neighbours.items():
            for v2 in v2list:
                tmpweight = 0 if v1 in nodes and v2 in nodes else 1
                graph.add_edge( v1, v2, weight=tmpweight  )
        distances = dict( netx.shortest_path_length( graph, weight="weight" ) )
        sourcenode = iter(nodes).__next__()
        for targetnode in graph.nodes():
            tmpdist = distances[sourcenode][targetnode]
            if tmpdist < alliance[ targetnode ][0]:
                alliance[ targetnode ] = ( tmpdist, i )
        del( graph )

    return { node: data[1] for node, data in alliance.items() }
                

def twographs_to_replacement( graph1, graph2, startnode, changedline_id ):
    from extrasfornetworkx import generate_replacement_from_graphs, \
                                AddedToUncommonNodes
    nodelabels1 = graph1.get_nodeattributelabel()
    edgelabels1 = graph1.get_edges_with_labels()
    startnode1, endnode1 = graph1.get_startstitch(), graph1.get_endstitch()
    nodelabels2 = graph2.get_nodeattributelabel()
    edgelabels2 = graph2.get_edges_with_labels()
    startnode2, endnode2 = graph2.get_startstitch(), graph2.get_endstitch()
    starttranslation = {startnode1:startnode2, endnode1:endnode2}
    logger.debug("input for extrasfornetworkx.generate_replacement_from"
                "_graphs: %s, %s, %s, %s, %s " % (nodelabels1, edgelabels1, \
                nodelabels2, edgelabels2, starttranslation ) )
    try:
        repl1, repl2, common_nodes = generate_replacement_from_graphs(\
                                    nodelabels1, edgelabels1,\
                                    nodelabels2, edgelabels2, \
                                    starttranslation )
        return tuple(  repl1 ), \
                tuple(  repl2 ), \
                tuple( (n1, n2) for n1, n2 in common_nodes )
    except AddedToUncommonNodes as err:
        repl1 = err.replacement_nodes_in_old
        repl2 = err.replacement_nodes_in_new
        common_nodes = err.same_nodes
        translator = { a:b for a, b in err.same_nodes }
    leftnodes1, leftnodes2, startnode1_left, leftindex, \
            rightnodes1, rightnodes2, startnode1_right, rightindex \
            = separate_wholegraphs_to_leftright_insulas( \
                    repl1, repl2, translator, \
                    graph1, graph2, changedline_id )
    brubru1 = set(nodelabels1.keys()).difference(repl1)
    brubru2 = set(nodelabels2.keys()).difference(repl2)
    a1 = compareGraph(*get_subgraph( brubru1, nodelabels1, edgelabels1 ))
    a2 = compareGraph(*get_subgraph( brubru2, nodelabels2, edgelabels2 ))
    l1 = compareGraph(*get_subgraph( brubru1.intersection(leftnodes1), nodelabels1, edgelabels1 ))
    l2 = compareGraph(*get_subgraph( brubru2.intersection(leftnodes2), nodelabels2, edgelabels2 ))
    r1 = compareGraph(*get_subgraph( brubru1.intersection(rightnodes1), nodelabels1,edgelabels1 ))
    r2 = compareGraph(*get_subgraph( brubru2.intersection(rightnodes2), nodelabels2,edgelabels2 ))
    if not( r1==r2 and l1==l2 ):
        raise Exception("couldnt separate left and right")
    
    return tuple(  repl1 ), \
            tuple(  repl2 ), \
            tuple( (n1, n2) for n1, n2 in common_nodes )


def get_subgraph( nodes, nodeattr, edges ):
    sub_nodeattr = { n:attr for n, attr in nodeattr.items() if n in nodes }
    sub_edges = list( (v1, v2, label) for v1, v2, label in edges \
                    if v1 in nodes and v2 in nodes )
    return sub_nodeattr, sub_edges

class compareGraph():
    def __init__( self, nodelabels, edgelabels ):
        self.nodelabels = nodelabels
        self.edgelabels = edgelabels
    def __eq__( self, other ):
        if type(self) != type(other):
            return False
        return self.__hash__() == other.__hash__()
    def __hash__( self ):
        return efn.weisfeiler_lehman_graph_hash_attributearray( \
                                        self.nodelabels, self.edgelabels )



def _multi_sidesigint_handler( signal_received, frame ):
    print( "Exiting gracefully" )
    exit( 0 )

class multi_sidealterator():
    def __init__( self, side_alterator_list ):
        self.side_alterator_list = side_alterator_list

    @classmethod
    def generate_from_linetypelist( cls, asdf, starttranslator_list=None, \
                                    skip_by_exception=False, \
                                    pipe_for_interrupt=None, \
                                    timelimit = 300):
        """Method for automativ creation of multialterator"""
        if starttranslator_list is not None:
            q = list( starttranslator_list )
        else:
            q = []
        if pipe_for_interrupt is not None:
            if type(pipe_for_interrupt) == list:
                pipe_for_interrupt.append( q )

        try:
            maxlen = str(len(asdf))
        except TypeError:
            maxlen = "?"
        i = 0
        if timelimit is not None:
            sidealt_gen = timelimiter.limit_calctime( sidealterator.from_linetypes, 300 )
        else:
            sidealt_gen = sidealterator.from_linetypes
        for linetype_out, linetype_in, upedges_out, upedges_in, changedline_id \
                                                                    in asdf:
            i+=1
            logger.info( "alteration %i/%s with %i found alterators" \
                            %(i,maxlen, len(q)))
            logger.debug( f"at line {changedline_id}; linetypes: {linetype_out}" )
            try:
                #new = sidealterator.from_linetypes( \
                new = sidealt_gen(\
                        linetype_out, linetype_in, \
                        upedges_out, upedges_in, \
                        changedline_id, skip_if_in_list = q )
                q.append( new )
            except SkipGeneration:
                logger.info( "already in list - skip" )
            except timelimiter.TimeLimitExceeded:
                logger.info( "timelimit exceeded" )
            except (timelimiter.NoDataProduced, Exception) as err:
                if not skip_by_exception:
                    raise
                else:
                    logger.info( "error, when trying to create next alterator" )
                    logger.debug( err )
        return cls( q )

    @classmethod
    def from_xml( cls, xmlstring ):
        """from given xmlstring"""
        from extrasfornetworkx import xml_config
        ET.register_namespace( "asd", xml_config.namespace )
        ET.register_namespace( "grml", xml_config.namespace_graphml )
        ET.register_namespace( "xsi", xml_config.namespace_xsi )

        verbesserer_xml = ET.fromstring( xmlstring )
        try:
            return cls.from_xmlobject( verbesserer_xml )
        except Exception as err:
            raise Exception(xmlstring) from err

    def replace_in_graph( self, graph, changeline ):
        """mainmethod

        :param graph: Graph to alterate
        :type graph: :py:class:`createcloth.strickgraph.strickgraph`
        :param changeline: Line to alterate
        :type changeline: int
        """
        lever = False
        row = graph.get_rows()[ changeline ]
        nodeattributes = graph.get_nodeattributes()
        edgeswithlabel = graph.get_edges_with_labels()
        for alt in self.side_alterator_list:
            try:
                graph = alt.replace_in_graph( graph, changeline, row=row, nodeattributes=nodeattributes, edgeswithlabel=edgeswithlabel )
                lever = True
                break
            except FindError:
                pass
        if not lever:
            raise FindError( changeline )
        return graph


    def toxmlelem( self ):
        """to xml element

        :rtype: xml.etree.ElementTree.Element
        """
        raise Exception()

    def to_xml( self, encoding="utf-8" ):
        """to xmlstring

        :param encoding: same as xml.etree.ElementTree.tostring
        :type encoding: str
        """
        from extrasfornetworkx import xml_config
        ET.register_namespace( "asd", xml_config.namespace )
        ET.register_namespace( "grml", xml_config.namespace_graphml )
        ET.register_namespace( "xsi", xml_config.namespace_xsi )
        elemroot = self.toxmlelem()
        xmlbytes = ET.tostring( elemroot, encoding=encoding )
        xmlstring = xmlbytes.decode( encoding )
        return xmlstring

def get_innerborder( sub_nodelist, graph ):
    """return border nodes within sub_nodelist"""
    neighbours = {}
    for v1, v2, label in graph.get_edges_with_labels():
        neighbours.setdefault( v1, list() ).append( v2 )
        neighbours.setdefault( v2, list() ).append( v1 )

    tmp_neighbours = set( it.chain(*(neighbours[n] for n in sub_nodelist)))
    neighs = tuple( tmp_neighbours.difference(sub_nodelist) )

    tmp_neighbours = set( it.chain(*(neighbours[n] for n in neighs)))
    return tuple( tmp_neighbours.intersection(sub_nodelist) )
