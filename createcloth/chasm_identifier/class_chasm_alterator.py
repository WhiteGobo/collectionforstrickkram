from .. import verbesserer
from . import method_classify as mcc
import xml.etree.ElementTree as ET
import extrasfornetworkx as efn
import time
from ..strickgraph import strickgraph
from .import customalterator_tools as utils
import itertools as it
from extrasfornetworkx import alterator


class chasm_alterator:
    directional = True
    @classmethod
    def _extract_info_from_graph( cls, inputgraph ):
        """This should be implemented, depending on the the
        used graph

        :returns: Node- and edgeattributes, also information
                    used by cls.find_startpoints
        return nodeattr, edgeattr, chasm_properties
        :rtype: ( dict, list, mcc.chasm_properties )
        :todo: implemention according to startinfo_container and
                    type of inputgraph
        """
        try:
            chasm_properties: mcc.chasm_properties \
                                = mcc.classify( inputgraph )
        except Exception as err:
            raise ValueError( "no chasm findable" ) from err

        nodeattr = inputgraph.get_nodeattributes()
        edgeattr = [ (v1, v2, (label,)) for v1, v2, label \
                                        in inputgraph.get_edges_with_labels() ]

        #extrainformation_for_startpointfinder = foo(inputgraph)
        return nodeattr, edgeattr, chasm_properties


    class startinfo_container:
        def __init__( self, side ):
            assert side in ("left", "right", "bottom" )
            self.side = side
        def find_startpoint( self, chasm_properties, \
                                alterated_row ):
            """Find Startpoint of alteration
 
            :type alterated_row: int
            :param alterated_row:
            """
            if alterated_row-1 > len( chasm_properties.leftside ):
                raise IndexError( "try to alterate in line, where no chasm is" )
            if self.side=="left":
                if alterated_row == 0:
                    raise ValueError()
                row = chasm_properties.leftside[ alterated_row-1 ]
                startpoint = row[0]
            elif self.side=="right":
                if alterated_row == 0:
                    raise ValueError()
                row = chasm_properties.rightside[ alterated_row-1 ]
                startpoint = row[0]
            elif self.side=="bottom":
                if alterated_row != 0:
                    raise ValueError()
                row = chasm_properties.bottom
                startpoint = row[0]
            return startpoint
        @classmethod
        def gen_in_replacement( cls, alterated_nodes_from_inputgraph, \
                                chasm_properties, alterated_row ):
            """Find persistent data for findstartpointmethod
 
            :param chasm_properties:
            :type chasm_properties:
            """
            assert alterated_row > 0
            leftrow = chasm_properties.leftside[ alterated_row-1 ]
            rightrow = chasm_properties.rightside[ alterated_row-1 ]
            in_left = any( n in leftrow for n in alterated_nodes_from_inputgraph )
            in_right = any( n in rightrow for n in alterated_nodes_from_inputgraph )
            if in_left and not in_right:
                side = "left"
            elif not in_left and in_right:
                side = "right"
            else:
                raise ValueError( f"couldnt identify on which side "
                        "alteration left/right: ({in_left}/{in_right})")
            return cls( side )
 
        def to_xml( self, encoding="utf8" ):
            """
            :returns: xml-string from which startinfo can be generated
            :rtype: str
            """
            ET.register_namespace( "asd", efn.xml_config.namespace )
            elemroot = ET.Element( efn.xml_config.startpointinfo )
            elemroot.attrib[ "side" ] = self.side
            xmlbytes = ET.tostring( elemroot, encoding=encoding )
            xmlstring = xmlbytes.decode( encoding )
            return xmlstring
        @classmethod
        def from_xml( cls, xmlstring ):
            ET.register_namespace( "asd", efn.xml_config.namespace )
            elemroot = ET.fromstring( xmlstring )
            assert elemroot.tag == efn.xml_config.startpointinfo, (elemroot.tag, efn.xml_config.startpointinfo)
            side = elemroot.attrib[ "side" ]
            assert side in ("left", "right" )
            return cls( side )

    def __init__( self, alterator_with_startpointinfo_list, notes=None ):
        self.startpointinfolist: List[startinfo_container] = []
        self.alteratorlist: List[alterator] = []
        for startpointinfo, alt in alterator_with_startpointinfo_list:
            self.startpointinfolist.append( startpointinfo )
            self.alteratorlist.append( alt )
        self.notes = str(notes)


    def replace_graph( self, target_strickgraph, chasmrow ):
        nodeattr, edgeattr, chasm_properties = self._extract_info_from_graph( \
                                            target_strickgraph )
        chasmrow = chasmrow % (chasm_properties.crack_height+1)
        starts = [ startinfo.find_startpoint( chasm_properties, chasmrow )\
                            for startinfo in self.startpointinfolist ]
        for start, part_alterator in zip( starts, self.alteratorlist ):
            nodeattr, edgeattr = part_alterator.replace_graph( nodeattr, \
                                            edgeattr, start )
        nodeattr = { n: {"stitchtype":d[0], "side":d[1]} \
                            for n, d in nodeattr.items() }
        edgeattr = [ (v1, v2, d[0]) for v1, v2, d in edgeattr ]
        return strickgraph( nodeattr, edgeattr )

        raise Exception( "wrong implementation" )
        try:
            chasm_properties = mcc.classify( target_strickgraph )
        except Exception as err:
            raise ValueError( "no chasm findable" ) from err
        if chasmrow > chasm_properties.rows or chasmrow < chasm_properties.rows:
            raise ValueError( "chasm not deep enough" )
        chasmrow = chasmrow % chasm_properties.crack_height
        if chasmrow == 0:
            len_bottom = len( chasm_properties.bottom )
            startpoint = chasm_properties.bottom[ int(len_bottom/2) ]
            return self._replace_graph_bottom
        else:
            left_anchor = chasm_properties.leftside[ chasmrow ]
            right_anchor = chasm_properties.rightside[ chasmrow ]
            return self._replace_graph_sides()

    def _replace_graph_bottom( self, target_strickgraph, startpoint ):
        pass
    def _replace_graph_sides( self, target_strickgraph, left_anchor, right_anchor ):
        pass

    @classmethod
    def from_graphdifference( cls, strick_in, strick_out, difference_line,\
                                    maximum_uncommon_nodes=10, \
                                    timelimit=None, soft_timelimit=0, \
                                    soft_maximum_uncommon_nodes=None ):
        """Generates alterator which transforms strick_in to strick_out

        """
        nodeattr1, edgeattr1, chasm_properties \
                            = cls._extract_info_from_graph( strick_in )
        nodeattr2, edgeattr2, _ = cls._extract_info_from_graph( strick_out )

        extraoptions = {}
        if timelimit is not None:
            extraoptions["timelimit"] = float( timelimit )
        trans_gen = efn.optimize_uncommon_nodes( \
                        nodeattr1, edgeattr1, \
                        nodeattr2, edgeattr2, **extraoptions )

        minimum_common_nodes = max( len(nodeattr1),len(nodeattr2) ) \
                        - maximum_uncommon_nodes
        if soft_maximum_uncommon_nodes is not None:
            extraoptions[ "soft_minimum_common_nodes" ] \
                        = max( len(nodeattr1), len(nodeattr2) ) \
                        - soft_maximum_uncommon_nodes
            extraoptions[ "soft_timelimit" ] = soft_timelimit
        translator = filter_translators( trans_gen, \
                        minimum_common_nodes, **extraoptions )

        neighbours1 = utils.neighs_from_edges( edgeattr1 )
        neighbours2 = utils.neighs_from_edges( edgeattr2 )
        trans_insulas1 = utils.get_insulas( translator.keys(), neighbours1 )
        translator = { key: translator[key] \
                    for key in max( trans_insulas1, key=len ) }

        subgraph_pairs = utils.separate_to_2_subgraphpairs( translator, \
                            neighbours1, neighbours2 )

        gen_startinfo = lambda x: \
                        cls.startinfo_container.gen_in_replacement( x,
                                chasm_properties, difference_line )
        startinfos = [ gen_startinfo( n1 ) for n1, _ in subgraph_pairs ]
        startpoints = [ stinfo.find_startpoint( chasm_properties, difference_line ) for stinfo in startinfos ]

        alterator_list = []
        def alt_gen( n1, n2, n1_startpoint ):
            return utils.create_single_alterator( nodeattr1, edgeattr1, \
                                            nodeattr2, edgeattr2, \
                                            n1, n2, translator, n1_startpoint, cls.directional )
        for startpoint, info_to_find_startpoint, pair \
                            in zip( startpoints, startinfos, subgraph_pairs ):
            nodes1, nodes2 = pair
            part_alterator = alt_gen( nodes1, nodes2, startpoint )
            alterator_list.append( (info_to_find_startpoint, part_alterator) )
        return cls( alterator_list )

        raise Exception()
        nodeattr1 = strick_in.get_nodeattributes()
        edgeattr1 = [ (v1, v2, (label,)) \
                        for v1, v2, label \
                        in strick_in.get_edges_with_labels() ]
        nodeattr2 = strick_out.get_nodeattributes()
        edgeattr2 = [ (v1, v2, (label,)) for v1, v2, label \
                        in strick_out.get_edges_with_labels() ]

        extraoptions = {}
        if timelimit is not None:
            extraoptions[ "timelimit" ] = timelimit

        trans_gen = efn.optimize_uncommon_nodes( nodeattr1, edgeattr1,\
                            nodeattr2, edgeattr2, **extraoptions )
        minimum_common_nodes = max( \
                            len(nodeattr1)-maximum_uncommon_nodes, \
                            len(nodeattr2)-maximum_uncommon_nodes )
        if soft_maximum_uncommon_nodes is not None:
            extraoptions[ "soft_minimum_common_nodes" ] = max( \
                            len(nodeattr1)-soft_maximum_uncommon_nodes, \
                            len(nodeattr2)-soft_maximum_uncommon_nodes )
            extraoptions[ "soft_timelimit" ] = soft_timelimit

        translator = filter_translations( trans_gen, minimum_common_nodes, \
                            **extraoptions )
        raise Exception( translator )
        #Anchor1

        return cls.with_common_nodes( nodeattr1, edgeattr1, \
                            nodeattr2, edgeattr2, translator )

    @classmethod
    def from_xml( cls, xmlstring ):
        ET.register_namespace( "asd", efn.xml_config.namespace )
        ET.register_namespace( "grml", efn.xml_config.namespace_graphml )
        ET.register_namespace( "xsi", efn.xml_config.namespace_xsi )

        xml_elem = ET.fromstring( xmlstring )
        
        full_name = efn.xml_config.ersetzung
        if full_name != xml_elem.tag:
            raise ValueError( f"wrong xmlobject, need {full_name}" )

        extraoptions = {}
        noteelement = xml_elem.find( efn.xml_config.notes )
        if noteelement is not None:
            extraoptions["notes"] = noteelement.text

        all_alterators = xml_elem.findall( efn.xml_config.ersetzung )
        all_startpointinfo = xml_elem.findall( efn.xml_config.startpointinfo )
        alts = [None] * len(all_alterators )
        starts = [None]*len(all_startpointinfo)
        assert len(alts) == len(starts)
        for alt_elem in all_alterators:
            index = int( alt_elem.attrib["index"] )
            alts[ index ] = alterator.from_xml( ET.tostring(alt_elem) )
        for start_elem  in all_startpointinfo:
            index = int( start_elem.attrib["index"] )
            starts[ index ] = cls.startinfo_container.from_xml( ET.tostring(start_elem) )
        return cls( zip( starts, alts ), **extraoptions )


        assert len( all_alterators ) == 2
        raise Exception( [ alt.attrib for alt in all_alterators] )
        leftright_alterators = { alt.attrib["side"]: alt \
                                for alt in all_alterators }
        assert leftright_alterators.keys() == {"left", "right" } 
        leftindex = int( leftright_alterators["left"].attrib["index"] )
        leftalt_str = ET.tostring( leftright_alterators["left"] )
        left_verbesserer = strickalterator.fromxml( leftalt_str )

        rightindex = int( leftright_alterators["right"].attrib["index"] )
        rightalt_str = ET.tostring( leftright_alterators["right"] )
        right_verbesserer = strickalterator.fromxml( rightalt_str )
        return cls( left_verbesserer, leftindex, right_verbesserer, rightindex, \
                                                            **extraoptions )

    def to_xml( self, encoding="utf8" ):
        ET.register_namespace( "asd", efn.xml_config.namespace )
        ET.register_namespace( "grml", efn.xml_config.namespace_graphml )
        ET.register_namespace( "xsi", efn.xml_config.namespace_xsi )

        elemroot = ET.Element( efn.xml_config.ersetzung )
        for i, alt in enumerate( self.alteratorlist ):
            xmlstr = alt.to_xml()
            elemroot.append( ET.fromstring( xmlstr ) )
            elemroot[-1].attrib[ "index" ] = str(i)
        for i, startinfo in enumerate( self.startpointinfolist ):
            xmlstr = startinfo.to_xml()
            elemroot.append( ET.fromstring( xmlstr ) )
            elemroot[-1].attrib[ "index" ] = str(i)

        if self.notes is not None:
            notes = ET.SubElement( elemroot, efn.xml_config.notes )
            notes.text = self.notes

        xmlbytes = ET.tostring( elemroot, encoding=encoding )
        xmlstring = xmlbytes.decode( encoding )
        return xmlstring
        raise NotImplementedError()

def filter_translators( trans_gen, minimum_common_nodes, \
                            soft_minimum_common_nodes = None, \
                            soft_timelimit=None, timelimit=150 ):
    starttime = time.time()
    besttrans_length = 0
    best_translator: dict = {}

    for translator in trans_gen:
        elapsed_time = time.time() - starttime
        try:
            if len(translator) > besttrans_length:
                best_translator = translator
                besttrans_length = len( best_translator )
        except TypeError: #translator can be None
            pass

        if soft_minimum_common_nodes is not None:
            cond1 = besttrans_length > soft_minimum_common_nodes\
                            and elapsed_time > soft_timelimit
        else:
            cond1 = False
        cond2 = besttrans_length > minimum_common_nodes \
                            and elapsed_time > timelimit
        if cond1 or cond2:
            return best_translator
        elif timelimit is not None:
            if elapsed_time > timelimit:
                break
    raise cmultiver.SkipAlteration( "no usable translation" )
