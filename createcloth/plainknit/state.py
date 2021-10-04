from typing import Iterable
import logging
from ..strickgraph.load_stitchinfo import myasd as glstinfo
logger = logging.getLogger( __name__ )
from collections import Counter
class rowstate():
    def __init__( self, name:str, identifier, downupdifference=None ):
        self.__name__ = name
        self.identifier = identifier
        if downupdifference is None:
            self._downupdifference = (0,)
        elif type( downupdifference ) == int:
            self._downupdifference = (downupdifference, )
        elif type( downupdifference ) == str:
            q = { "positive":range(3, 6), "negative":range(-3,-6,-1)}
            try:
                self._downupdifference = tuple(q[downupdifference])
            except KeyError as err:
                raise KeyError( "string downupdifference must be one" \
                                + f"of these: {tuple(q.keys())}" ) from err
        else:
            try:
                tmparray = iter( downupdifference )
                self._downupdifference( tuple( tmparray ) )
            except TypeError:
                raise

    def get_downupdifference_examples( self ):
        return self._downupdifference

    def __str__( self ):
        return self.__name__
    def create_example_row( self, downedges, upedges ) :
        assert downedges is None or type( downedges ) == int, f"downedges must be int, {downedges}"
        assert upedges is None or type( upedges ) == int, f"upedges must be int {upedges}"
        return self.identifier.create_row( downedges, upedges )
    def identify( self, line_stitchtypes: Iterable[ str ] ):
        return self.identifier( line_stitchtypes )

    @classmethod
    def with_variabledifference( cls, name:str, identifier, \
                                        downupdifference_positive = True ):
        q = "positive" if downupdifference_positive else "negative"
        return cls( name, identifier, downupdifference=q )

    @classmethod
    def with_static_downupdifference( cls, name:str, identifier, \
                                                downupdifference:int):
        return cls( name, identifier, downupdifference=downupdifference )

    def calc_edgedifference( self, length, nextlength, lastlength ):
        self.identifier


class linetype_identifier():
    pass

class linetype_identifier_simple( linetype_identifier ):
    def __init__( self, default_stitchtype:str ):
        self.default_stitchtype = default_stitchtype
        self.stitchinfo = glstinfo
    def __call__( self, line_stitchtypes: list[ str ] ):
        if len( line_stitchtypes ) < 8:
            return False
        allstitches = set( line_stitchtypes )
        return allstitches == set(( self.default_stitchtype, ))

    def _get_stitchnumber_from_edges( self, downedges, upedges ):
        test = ( downedges == upedges,\
                upedges == 0 or upedges is None,\
                downedges == 0 or downedges is None, \
                )
        if test[0] and not (test[1] or test[2]):
            return downedges
        elif test[1] and not test[2]:
            return downedges
        elif test[2] and not test[1]:
            return upedges
        else:
            raise Exception( "simple identifier can only work with only "\
                                "up- or downedges or an equal number of edges",\
                                downedges, upedges )

    def create_row( self, downedges=None, upedges=None, **args ):
        length = self._get_stitchnumber_from_edges( downedges, upedges )
        #if length < 8:
        #    raise Exception( "create_row must be at least 8 stitches wide")
        if args:
            logger.debug( "create_row got unnused arguments :{args}" )
        return [ self.default_stitchtype ]*length


class linetype_identifier_fourborderstitches( linetype_identifier ):
    def __init__( self, default_stitchtype:str, \
                        fourborder_stitchtype_right: Iterable[str] ):
        self.default_stitchtype = default_stitchtype
        self.fourborder_stitchtype_right = tuple( fourborder_stitchtype_right )
        self.fourborder_stitchtype_left \
                        = tuple( reversed(self.fourborder_stitchtype_right) )
        if len(self.fourborder_stitchtype_right ) != 4:
            raise Exception( "given bordertypes must be 4 str" )
        self.contained_stitchtypes = set(( default_stitchtype, )) \
                                    .union(set( fourborder_stitchtype_right ))
        self.border_downedges = 2 * sum( glstinfo.downedges[q] \
                                    for q in fourborder_stitchtype_right)
        self.border_upedges = 2 * sum( glstinfo.upedges[q] \
                                    for q in fourborder_stitchtype_right)

    def __call__( self, line_stitchtypes: list[ str ] ):
        if len( line_stitchtypes ) < 8:
            return False
        middlestitches = set( line_stitchtypes[4:-4] )
        return all((\
                middlestitches.difference(( self.default_stitchtype, )) ==set(),
                line_stitchtypes[:4] != self.fourborder_stitchtype_left,
                line_stitchtypes[-4:] != self.fourborder_stitchtype_right,
                ))

    def create_row( self, downedges=None, upedges=None, **args ):
        length = downedges - self.border_downedges + 8
        if length < 8:
            raise Exception( "create_row must be at least 8 stitches wide", length, downedges, self.border_downedges)
        if args:
            logger.debug( "create_row got unnused arguments :{args}" )
        return list( self.fourborder_stitchtype_left ) \
                + [ self.default_stitchtype ]*( length - 8 ) \
                + list( self.fourborder_stitchtype_right)\

class linetype_identifier_oneside_increase( linetype_identifier ):
    def __init__( self, default_stitchtype:str, border_stitchtype:str, \
                                                            right=True ):
        self.default_stitchtype = default_stitchtype
        self.border_stitchtype = border_stitchtype
        self.right = right
        self.contained_stitchtypes = set(( default_stitchtype, \
                                            border_stitchtype ))

    def __call__( self, line_stitchtypes: list[ str ] ):
        if len( line_stitchtypes ) < 8:
            return False
        mycounter = Counter( line_stitchtypes )
        if mycounter.keys() != self.contained_stitchtypes:
            return False
        length_border = mycounter[ self.border_stitchtype ]
        if self.right:
            mainstitches = set( line_stitchtypes[ : -length_border ] )
        else:
            mainstitches = set( line_stitchtypes[ length_border: ] )
        return mainstitches == set(( self.default_stitchtype, ))

    def create_row( self, downedges=None, upedges=None, **args ):
        difference = upedges - downedges
        if difference < 1 or upedges < 8:
            raise Exception( "create_row must be at least 8 stitches wide "\
                            +"and there must be more upedges than downedges")
        leftarray = [ self.border_stitchtype ] * difference \
                + [ self.default_stitchtype ] * downedges
        if self.right:
            leftarray.reverse()
        return leftarray

class linetype_identifier_oneside_decrease( linetype_identifier ):
    def __init__( self, default_stitchtype:str, border_stitchtype:str, \
                                                            right=True ):
        self.default_stitchtype = default_stitchtype
        self.border_stitchtype = border_stitchtype
        self.right = right
        self.contained_stitchtypes = set(( default_stitchtype, \
                                            border_stitchtype ))

    def __call__( self, line_stitchtypes: list[ str ] ):
        if len( line_stitchtypes ) < 8:
            return False
        mycounter = Counter( line_stitchtypes )
        if mycounter.keys() != self.contained_stitchtypes:
            return False
        length_border = mycounter[ self.border_stitchtype ]
        if self.right:
            mainstitches = set( line_stitchtypes[ : -length_border ] )
        else:
            mainstitches = set( line_stitchtypes[ length_border: ] )
        return mainstitches == set(( self.default_stitchtype, ))

    def create_row( self, downedges=None, upedges=None, **args ):
        difference = downedges - upedges
        if difference < 1 or downedges < 8:
            raise Exception( "create_row must be at least 8 stitches wide "\
                            +"and there must be more downedges than upedges")
        leftarray = [ self.border_stitchtype ] * difference \
                + [ self.default_stitchtype ] * upedges
        if self.right:
            leftarray.reverse()
        return leftarray
