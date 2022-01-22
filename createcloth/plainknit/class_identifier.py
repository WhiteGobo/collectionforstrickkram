from . import method_isplain as mip
from . import create_example_strickgraphs as ces
from .rowstates import start, end, leftplane, rightplane, \
                    lefteaves, righteaves, enddecrease, \
                    plain, increase, decrease

from ..strickgraph import strickgraph
from ..stitchinfo import basic_stitchdata as glstinfo
def create_graph_from_linetypes( linetypes, upedges, startside="right" ):
    """Create graph only from linetypes

    :param linetypes:
    :type linetypes: Iterable[ rowstates ]
    :param upedges: List of upedges
    :type upedges: Iterable[ int ]
    :param startside: Side of first row of created strickgraph. Attribute 
                to plainknit
    :type startside: str
    :returns: Strickgraph tailored to given attributes
    :rtype: strickgraph
    :todo: there is double?? in create_verbesserer
    """
    sides = ("right", "left") if startside=="right" else ("left", "right")
    downedges = [ None, *upedges ]
    upedges = [ *upedges, None ]
    iline = range(len(downedges))
    allinfo = zip( linetypes, downedges, upedges, iline )
    try:
        graph_man = [ s.create_example_row( down, up, side=sides[i%2] ) \
                                for s, down, up, i in allinfo ]
    except Exception as err:
        raise Exception( [str(a) for a in linetypes], downedges, upedges, iline, startside ) from err
        raise err
    graph = strickgraph.from_manual( graph_man, glstinfo, \
                                manual_type="machine", startside=startside)
    return graph


def plainknit_strickgraph_identifier_a( target_strickgraph ):
    """Identifier of strickgraph as plainknit

    :param target_strickgraph:
    :type target_strickgraph: createcloth.strickgraph
    :rtype: Dict
    :returns: attributes, 'linetypes', 'startside' and 'upedges'
    """
    nodestitchtype = target_strickgraph.get_nodeattr_stitchtype()
    rows = target_strickgraph.get_rows()
    nodes_at_sidemargins = target_strickgraph.get_sidemargins()
    node_sides = target_strickgraph.get_nodeattr_side()
    return plainknit_strickgraph_identifier( nodestitchtype, node_sides, \
                                                rows, nodes_at_sidemargins )

def plainknit_strickgraph_identifier( nodestitchtype, node_sides, rows, \
                                                    nodes_at_sidemargins ):
    return_attributes = {}
    identifier_row = ( start, end, leftplane, rightplane, \
                        lefteaves, righteaves, enddecrease, \
                        plain, increase, decrease )
    idlinefoo = lambda line: ( i for i in identifier_row \
                                if i.identify(line)).__next__()
    row_to_types = lambda line: [ nodestitchtype[s] for s in line ]
    try:
        row_stitchtypes = [ row_to_types(row) for row in rows ]
        row_states = [ idlinefoo( row ) for row in row_stitchtypes ]
    except StopIteration as err:
        raise TypeError( "Given strickgraph isnt plain" ) from err
    return_attributes[ "linetypes" ] = row_states
    return_attributes[ "startside" ] = node_sides[ rows[0][0] ]

    get_upedges = lambda st_line: sum( glstinfo.upedges[ st_type ] \
                                    for st_type in st_line )
    upedges = [ get_upedges( row ) for row in row_stitchtypes ]
    upedges = upedges[ :-1 ]
    return_attributes[ "upedges" ] = upedges
    return return_attributes

