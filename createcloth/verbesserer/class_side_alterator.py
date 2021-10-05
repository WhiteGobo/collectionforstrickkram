from .verbesserer_class import FindError
import xml.etree.ElementTree as ET
import logging
import extrasfornetworkx as efn
logger = logging.getLogger( __name__ )

XML_SIDEALTERATOR_NAME = "sidealterator"

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

    def replace_in_graph( self, strickgraph, linenumber ):
        """mainmethod replkaces in graph at given line
        :raises: FindError
        """
        row = strickgraph.get_rows()[ linenumber ]
        startnodeleft = row[ self.leftstartindex ]
        startnoderight = row[ self.rightstartindex ]

        logger.debug( "checking if graph ist replaceable" )
        cond1 = self.alterator_left.isreplaceable( strickgraph, startnodeleft )
        cond2 = self.alterator_right.isreplaceable( strickgraph,startnoderight )
        logger.debug( f"left-replaceble: {cond1}, right-replacable: {cond2}" )
        if cond1 and cond2:
            logger.debug( "replaceleft" )
            self.alterator_left.replace_in_graph( strickgraph, startnodeleft )
            logger.debug( "replaceright" )
            self.alterator_right.replace_in_graph( strickgraph, startnoderight )
        else:
            raise FindError()
    
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
        logger.info( "find graphdifferencewhole" )
        difference_graph1, difference_graph2, translator \
                                = twographs_to_replacement( \
                                source_strickgraph, target_strickgraph, \
                                startnode, changedline_id )
        logger.info( f"difference input: {difference_graph1}" )
        logger.info( f"difference output: {difference_graph2}" )
        #print("diffs:\n", sorted(difference_graph1), "\n\n", sorted(difference_graph2), "\n" )
        translator = { a:b for a, b in translator }
        leftnodes1, leftnodes2, startnode1_left, leftindex, \
                rightnodes1, rightnodes2, startnode1_right, rightindex \
                = separate_wholegraphs_to_leftright_insulas( \
                        difference_graph1, difference_graph2, translator, \
                        source_strickgraph, target_strickgraph, changedline_id )
        mykey = lambda x: x if type(x)==tuple \
                        else (x,) if type(x)==int \
                        else (0,)
        logger.info( f"startnodes l/r: {startnode1_right}, {startnode1_left}" )
        logger.info( "leftnodes1: %s" %( sorted(leftnodes1, key=mykey) ))
        logger.info( "leftnodes2: %s" %( sorted(leftnodes2, key=mykey) ))
        logger.info( "rightnodes1: %s" %( sorted(rightnodes1, key=mykey) ))
        logger.info( "rightnodes2: %s" %( sorted(rightnodes2, key=mykey) ))

        #print("="*75)
        #print("generate leftrightverbesserer" )
        startnode2_left = translator[ startnode1_left ]
        startnode2_right = translator[ startnode1_right ]
        lefttrans = { a:b for a, b in translator.items() if a in leftnodes1 }
        #print( f"correspondingleft: {leftindex}, {startnode1_left}, {startnode2_left}\n", sorted(leftnodes1), "\n",sorted(leftnodes2),"\n\n")
        #print( "lefttrans:", lefttrans, "\n")
        logger.info("create left alterator")
        logger.info( f"nodes1: {leftnodes1}")
        logger.info( f"nodes2: {leftnodes2}")
        a = generate_verbesserer_asdf( \
                                source_strickgraph, target_strickgraph, \
                                leftnodes1, leftnodes2, \
                                startnode1_left, startnode2_left,
                                lefttrans )
        #print("-"*75)
        #print("oldnodes: ", sorted(a.oldgraph_nodeattributes.items()) )
        #print("newnodes: ", a.newgraph_nodeattributes )
        #print("idpath: ", a.oldgraph_identificationpath )
        #print("edgeattr: ", a.newgraph_edges_with_label )
        logger.info("create right alterator")
        righttrans = { a:b for a, b in translator.items() if a in rightnodes1 }
        logger.info( f"nodes1: {rightnodes1}")
        logger.info( f"nodes2: {rightnodes2}")
        b = generate_verbesserer_asdf( \
                                source_strickgraph, target_strickgraph, \
                                rightnodes1, rightnodes2, \
                                startnode1_right, startnode2_right, \
                                righttrans )
        return cls( a, leftindex, b, rightindex )

def generate_verbesserer_asdf( graph1, graph2, \
                                subnodelist1, subnodelist2, \
                                startnode1, startnode2, starttranslation ):
    subgraph1 = graph1.subgraph( subnodelist1 )
    subgraph2 = graph2.subgraph( subnodelist2 )
    from extrasfornetworkx import generate_replacement_from_graphs, AddedToUncommonNodes
    nodelabels1 = subgraph1.get_nodeattributes()
    edgelabels1 = subgraph1.get_edgeattributelabels()
    nodelabels2 = subgraph2.get_nodeattributes()
    edgelabels2 = subgraph2.get_edgeattributelabels()
    from ..verbesserer.verbesserer_class import strickalterator
    return strickalterator.from_graph_difference(
                                        nodelabels1, edgelabels1,\
                                        nodelabels2, edgelabels2, \
                                        startnode1, \
                                        startnode2, \
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
                                        nodetrans2[startnode2], \
                                        translation )


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
    less_graph_nodes = less_graph.give_real_graph().nodes()
    great_graph_nodes = great_graph.give_real_graph().nodes()

    #find left and right side to replace with insulas
    connected_insulas = less_graph.get_connected_nodes( difference_graph1 )
    connected_insulas2 = great_graph.get_connected_nodes( difference_graph2 )
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
    for asdf in connected_insulas:
        for qwer in connected_insulas2:
            if not any( translator[q] in qwer \
                            for q in asdf if q in translator.keys() ):
                continue
            nearnodes = less_graph.get_nodes_near_nodes( asdf )
            nearnodes2 = great_graph.get_nodes_near_nodes( qwer )
            qgqg = lambda x: x[0]
            print( "translator: ", sorted(((a,b) for a,b in translator.items() if a in nearnodes or b in nearnodes2), key=qgqg) )
            print( "-"*75, "\nbrubru", qs(nearnodes), qs(nearnodes2) )
            try:
                startnode1_left, leftindex \
                    = ( (node, index) for node, index in leftside_nodes\
                    if node in asdf and node in translator ).__next__()
                startnode2_left = translator[ startnode1_left ]
                invtrans = inv( translator )
                leftnodes1 = set( invtrans[n] for n in nearnodes2 \
                                if n in invtrans ).union( nearnodes )
                leftnodes2 = set( translator[n] for n in nearnodes \
                                if n in translator ).union( nearnodes2 )
            except StopIteration:
                pass
            try:
                startnode1_right, rightindex \
                    = ( (node, index) for node,index in rightside_nodes\
                    if node in asdf and node in translator ).__next__()
                startnode2_right = translator[ startnode1_right ]
                invtrans = inv( translator )
                rightnodes1 = set( invtrans[n] for n in nearnodes2 \
                                if n in invtrans ).union( nearnodes )
                rightnodes2 = set( translator[n] for n in nearnodes \
                                if n in translator ).union( nearnodes2 )
                print("-"*75)
                print( "right1_common", qs([n for n in rightnodes1 if n in translator ]),"\n")
                print( "right1_uncommon", qs([n for n in rightnodes1 if n not in translator ]))
                print("-"*75)
                print( "right2_common", qs([n for n in rightnodes2 if n in invtrans ]),"\n")
                print( "right2_uncommon",qs([n for n in rightnodes2 if n not in invtrans ]),"\n")
            except StopIteration:
                pass
    try:
        return leftnodes1, leftnodes2, startnode1_left, leftindex, \
                rightnodes1, rightnodes2, startnode1_right, rightindex
    except NameError as err:
        raise NoLeftRightFound() from err



def twographs_to_replacement( graph1, graph2, startnode, changedline_id ):
    from extrasfornetworkx import generate_replacement_from_graphs, \
                                AddedToUncommonNodes
    nodelabels1 = graph1.get_nodeattributelabel()
    edgelabels1 = graph1.get_edgeattributelabels()
    nodelabels2 = graph2.get_nodeattributelabel()
    edgelabels2 = graph2.get_edgeattributelabels()
    try:
        repl1, repl2, common_nodes = generate_replacement_from_graphs(\
                                        nodelabels1, edgelabels1,\
                                        nodelabels2, edgelabels2, \
                                        {"start":"start", "end":"end"} )
        #                                {startnode: startnode} )
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
    raise Exception("should come to this")
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
    #print( nodelabels1, edgelabels1, nodelabels2, edgelabels2, nodetrans1[startnode], nodetrans2[startnode] )
    #print( antitrans1 )
    #print("-"*75)
    #print( antitrans2 )

    repl1, repl2, common_nodes = generate_replacement_from_graphs(\
                                        nodelabels1, edgelabels1,\
                                        nodelabels2, edgelabels2, \
                                        {nodetrans1[startnode]:\
                                        nodetrans2[startnode]} )
    return tuple( antitrans1[ node ] for node in repl1 ), \
            tuple( antitrans2[ node ] for node in repl2 ), \
            tuple( (antitrans1[n1], antitrans2[n2]) for n1, n2 in common_nodes )


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
