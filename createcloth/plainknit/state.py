from typing import Iterable
import logging
logger = logging.getLogger( __name__ )
from collections import Counter
class rowstate():
    def __init__( self, name:str, identifier ):
        self.__name__ = name
        self.identifier = identifier

    def __str__( self ):
        return self.__name__
    def create_example_row( self, length = 8) :
        return self.identifier.create_row( length )
    def identify( self, line_stitchtypes: Iterable[ str ] ):
        return self.identifier( line_stitchtypes )

id_array = [ "leftplane", "rightplane", "lefteaves", "righteaves", \
                "start", "end", "enddecrease", "plain", "increase", "decrease"]

class linetype_identifier():
    pass

class linetype_identifier_simple( linetype_identifier ):
    def __init__( self, default_stitchtype:str ):
        self.default_stitchtype = default_stitchtype
    def __call__( self, line_stitchtypes: list[ str ] ):
        if len( line_stitchtypes ) < 8:
            return False
        allstitches = set( line_stitchtypes )
        return allstitches == set(( self.default_stitchtype, ))
    def create_row( self, length, **args ):
        if length < 8:
            raise Exception( "create_row must be at least 8 stitches wide")
        if args:
            logger.debug( "create_row got unnused arguments :{args}" )
        return [ self.default_stitchtype ]*length


class linetype_identifier_fourborderstitches( linetype_identifier ):
    def __init__( self, default_stitchtype:str, \
                        fourborder_stitchtype_right: Iterable[str] ):
        self.default_stitchtype = default_stitchtype
        self.fourborder_stitchtype_right = tuple( fourborder_stitchtype_right )
        self.fourborder_stitchtype_left = reversed( \
                                        tuple( fourborder_stitchtype_right ))
        if len(self.fourborder_stitchtype_right ) != 4:
            raise Exception( "given bordertypes must be 4 str" )
        self.contained_stitchtypes = set(( default_stitchtype, )) \
                                    .union(set( fourborder_stitchtype_right ))

    def __call__( self, line_stitchtypes: list[ str ] ):
        if len( line_stitchtypes ) < 8:
            return False
        middlestitches = set( line_stitchtypes[4:-4] )
        return all((\
                middlestitches == set(( self.default_stitchtype, )),
                line_stitchtypes[:4] != self.fourborder_stitchtype_left,
                line_stitchtypes[-4:] != self.fourborder_stitchtype_right,
                ))
    def create_row( self, length, **args ):
        if length < 8:
            raise Exception( "create_row must be at least 8 stitches wide")
        if args:
            logger.debug( "create_row got unnused arguments :{args}" )
        return list( self.fourborder_stitchtype_right ) \
                + [ self.default_stitchtype ]*(length-8) \
                + list( self.fourborder_stitchtype_left)

class linetype_identifier_oneside( linetype_identifier ):
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

    def create_row( self, length, secondlength=2 ):
        if length < 8:
            raise Exception( "create_row must be at least 8 stitches wide")
        leftarray = [ self.border_stitchtype ] * secondlength \
                + [ self.default_stitchtype ] * length
        if self.right:
            leftarray.reverse()
        return leftarray
        
start = rowstate( "start", linetype_identifier_simple( "yarnover" ) )
end = rowstate( "end", linetype_identifier_simple( "bindoff" ) )
leftplane = rowstate( "leftplane", \
                linetype_identifier_oneside( "knit", "yarnover", right=False ) )
rightplane = rowstate( "rightplane", \
                linetype_identifier_oneside( "knit", "yarnover", right=True ) )
lefteaves = rowstate( "lefteaves", \
                linetype_identifier_oneside( "knit", "bindoff", right=False ) )
righteaves = rowstate( "righteaves", \
                linetype_identifier_oneside( "knit", "bindoff", right=True ) )
enddecrease = rowstate( "enddecrease", \
                linetype_identifier_fourborderstitches( "bindoff", \
                ["knit", "yarnover", "knit", "knit" ] ))
plain = rowstate( "plain", linetype_identifier_simple( "knit" ) )
increase = rowstate( "increase",
                linetype_identifier_fourborderstitches( "knit", \
                ["knit", "yarnover", "knit", "knit" ] ))
decrease = rowstate( "decrease",
                linetype_identifier_fourborderstitches( "knit", \
                ["knit", "k2tog", "knit", "knit" ] ))
