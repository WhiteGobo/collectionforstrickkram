from ..strickgraph import strickgraph
from ..stitchinfo import basic_stitchdata as glstinfo
import math

def generate_example( crack_height, crack_width, crack_arrays, height, width, \
                            startside = "left" ):
    man = []
    firstrow = "%iyo" %( width )
    man.append( firstrow )
    plainrow = "%ik" %( width )
    man.extend( [plainrow] * ( height - crack_height - 2 ))
    nplainstitches = width - crack_width
    leftn = math.ceil( nplainstitches/2 )
    rightn = math.floor( nplainstitches/2 )
    bottomrow = "%ik %ibo %ik" %( leftn, crack_width, rightn )
    man.append( bottomrow )
    thread = 1
    for i, ltype in zip( range( height-crack_height, height-1 ), crack_arrays ):
        leftn += { "plain":0, "increase":1, "decrease":-1}[ ltype ]
        rightn += { "plain":0, "increase":1, "decrease":-1}[ ltype ]
        left = ["k"] * leftn
        right = ["k"] * rightn
        left[ -2 ] = { "plain":'k', "increase":'yo', "decrease":'k2tog'}[ ltype ]
        right[ 1 ] = { "plain":'k', "increase":'yo', "decrease":'k2tog'}[ ltype ]
        line = " ".join( left + ["switch%i"%(thread)] + right )
        thread = (thread+1)%2
        man.append( line )
    line = " ".join( (["bo"]*leftn) + ["switch%i"%(thread)] + (["bo"]*rightn) )
    man.append( line )
    man = "\n".join( man )

    return strickgraph.from_manual( man, glstinfo )
