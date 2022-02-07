import networkx as netx
from collections.abc import Container, Mapping

from dataclasses import dataclass, field
@dataclass
class chasm_properties( Mapping ):
    crack_height: int
    crack_arrays: list
    crack_width: int
    crack_dwidth: list
    leftside: list = None #field( default_factory=list )
    rightside: list = None #field( default_factory=list )
    bottom: list = None #field( default_factory=list )
    def __iter__( self ):
        return iter( self.__dict__ )
    def __getitem__( self, x ):
        return self.__dict__[ x ]
    def __len__( self ):
        return 6
    def __eq__( self, other ):
        try:
            odict = dict(other)
            keys = ["crack_height", "crack_arrays", "crack_width"]
            keys_def = ["leftside", "rightside", "bottom" ]
            if set((*keys, *keys_def)).issuperset( odict.keys() ):
                return all( odict[key] == self.__dict__[key] for key in keys )\
                    and all( odict.get(key) == self.__dict__[key] \
                    for key in keys_def )
            else:
                return False
        except (KeyError, TypeError, ValueError):
            return False

    def dist( self, other ):
        rowdata = (self.leftside, other.leftside, self.rightside,
                other.rightside, self.bottomside, other.bottomside==None)
        if not (all( i is None for i in rowdata ) \
                or all( i is not None for i in rowdata )):
            raise ValueError()
        dheight = abs( self.crack_height - other.crack_height )
        darrays = sum( 0 if a==b else 1 \
                    for a,b in zip(self.crack_arrays, other.crack_arrays) )
        dwidth = abs( self.crack_width - other.crack_width )

        if all( i is not None for i in rowdata ):
            d=1
        else:
            d=0
        


class line_identifier( Container ):
    """

    :todo: bottomline identify must be changed
    """
    needed_spacing = 5
    def __contains__( self, x ):
        try:
            x = list(x)
        except Exception:
            return False
        if {"bindoff"} == set(x):
            return True

        lineiter = iter( x )
        firstknit_index = x.index( "knit" )
        if firstknit_index > 0:
            cond1 = set( x[ :firstknit_index ] ) == { "yarnover" }
            plainafter = x[ firstknit_index: firstknit_index+self.needed_spacing ]
            cond2 = set( plainafter ) == { "knit" }
            return all( cond1, cond2 )
        cond1 = x[0] == "knit"
        cond2 = x[1] in [ "knit", "decrease", "increase" ]
        ll = x[ 2: 2+self.needed_spacing ]
        cond3 = set(ll) == {"knit"}
        return all((cond1, cond2, cond3))
    def __getitem__( self, x ):
        x = list( x )
        assert self.__contains__( x ), x
        if set(x) == {"bindoff"}:
            return "top"
        elif x[1] == "knit":
            return "plain"
        elif x[1] == "decrease":
            return "decrease"
        elif x[1] == "increase":
            return "increase"
        raise Exception( "oops  something went wrong" )
    def get( self, x, default=None ):
        if x in self:
            return self.__getitem__( x )
        else:
            return default
    #def __iter__( self ):
    #    a = ["knit", "knit"] + ["knit"] * ( max_needed_for_identification - 2 )
    #    b = ["knit", "decrease"] + ["knit"] * ( max_needed_for_identification - 2 )
    #    c = ["knit", "increase"] + ["knit"] * ( max_needed_for_identification - 2 )
    #    yield a
    #    yield b
    #    yield c
    #def __len__( self ):
    #    return 3

class line_identifier_reversed( Mapping ):
    def __getitem__( self, x ):
        assert self.__contains__( x )
        if x[1] == "knit":
            return "plain"
        elif x[1] == "decrease":
            return "decrease"
        elif x[1] == "increase":
            return "increase"
        raise Exception( "oops  something went wrong" )
    #def get( self, x, default=None ):
    #    if x in self:
    #        return self.__getitem__( x )
    #    else:
    #        return default
    def __iter__( self ):
        for i in ("knit", "decrease", "increase"):
            yield i
    def __len__( self ):
        return 3

def classify( mystrickgraph ):
    rows = mystrickgraph.get_rows()
    stitchtypes = mystrickgraph.get_nodeattr_stitchtype()
    down, up, left, right = mystrickgraph.get_borders()

    chasm_stitches = [ s for s in up if s not in rows[-1] ]

    #asd = [ mystrickgraph.get_nodes_near_nodes( [q], 3 ) for q in chasm_stitches ]
    leftside, rightside, bottom = find_chasm_parts_as_stitchlist( mystrickgraph )
    leftside_sttype = [ [stitchtypes[q] for q in line] for line in leftside ]
    rightside_sttype = [ [stitchtypes[q] for q in line] for line in rightside ]

    line_map =  line_identifier()

    bottom_sttype = [ stitchtypes[q] for q in bottom ]
    if set( bottom_sttype ) != {'bindoff', 'knit'}:
        raise KeyError( "invalid strickgraph for chasmidentifier, bottom is strange", bottom_sttype )
    linetypes_left = [ line_map[i] for i in leftside_sttype ]
    linetypes_right =  [ line_map[i] for i in rightside_sttype ]
    if any( l!=r for l, r in zip( linetypes_left, linetypes_right )):
        raise KeyError( "invalid strickgraph for chasmidentifier, not symmetric" )

    crack_height = len( leftside_sttype )
    crack_arrays = tuple( reversed(linetypes_left) )#[:-1] )
    left_over_crack_stitch = leftside[ -1 ][0]
    right_over_crack_stitch = rightside[ -1 ][0]
    tmp_left_to_right = ( up.index( left_over_crack_stitch ), \
                            up.index( right_over_crack_stitch ) )
    crack_width = abs( tmp_left_to_right[0] - tmp_left_to_right[1] ) - 3
    bottom = [ x for x in bottom if x in up ]
    return chasm_properties( **{ "crack_height": crack_height, \
            "crack_arrays": crack_arrays, \
            "crack_width": crack_width, \
            "crack_dwidth": [0,1,2,3], \
            "leftside": leftside, \
            "rightside": rightside, \
            "bottom": bottom, \
            })

def find_chasm_parts_as_stitchlist( mystrickgraph ):
    """
    
    :todo: cant extract mystrickgraph to reduced informationinput, 
            because getnodes_near_nodes
    :todo: method seems very long
    """
    rows = mystrickgraph.get_rows()
    st_to_row = {}
    for i, row in enumerate( rows ):
        st_to_row.update( { st:i for st in row } )
    down, up, left, right = mystrickgraph.get_borders()
    edges = mystrickgraph.get_edges_with_labels()
    same_row_edges = [ (v1, v2) for v1, v2, _ in edges \
                        if st_to_row[v1] == st_to_row[v2] ]
    chasm_stitches = [ s for s in up if s not in rows[-1] ]
    #asd = mystrickgraph.get_nodes_near_nodes( chasm_stitches, 4 )
    G = netx.Graph()
    for v1, v2 in same_row_edges:
        #if all( v in asd for v in (v1, v2) ):
        G.add_edge( v1, v2 )
    S = [G.subgraph(c).copy() for c in netx.connected_components(G)]
    rowlines = [ singlegraph.nodes() for singlegraph in S ]
    qq = {}
    for ll in rowlines:
        ll = list(ll)
        #reduce to rows at chasm, uses up instead of chasm_stitches
        if any( v in up for v in ll ):
            i = st_to_row[ ll[0] ]
            qq.setdefault( i, [] ).append( ll )
    maxi = max(qq)
    i = min(qq)
    bottom = qq.pop( min(qq) )[0]
    bottom.sort( key=rows[i].index )
    left_chasm = [None] * len(qq)
    right_chasm = [None] * len(qq)
    for i, sublines in qq.items():
        mykey = lambda l: rows[i].index( l[0] )
        a,b = sorted( sublines, key = mykey )
        a.sort( key=rows[i].index, reverse=True )
        b.sort( key=rows[i].index )
        chasm_index = abs( maxi - i )
        left_chasm[ chasm_index ] = a
        right_chasm[ chasm_index ] = b

    return left_chasm, right_chasm, bottom
