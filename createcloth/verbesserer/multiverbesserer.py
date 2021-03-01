from extrasfornetworkx import multiverbesserer
from extrasfornetworkx import multiverbessererfromxml
from ..strickgraph.strickgraph_base import stricksubgraph
import itertools
import math

class StrickgraphVerbessererException( Exception ):
    def __init__( self, mymultiverbesserer, mystrickgraph, markednode, *args ):
        super().__init__( mymultiverbesserer, mystrickgraph, markednode, *args )
        self.usedverbesserer = mymultiverbesserer
        self.usedstrickgraph = mystrickgraph
        self.markednodeinstrickgraph = markednode

try:
    import matplotlib.pyplot as plt
    from ..visualizer.graph_2d import easygraph
    IMPORTEDMATPLOTLIB = True
except ModuleNotFoundError as err:
    IMPORTEDMATPLOTLIB = False
    #i want here to make import optional
    raise err


class strick_multiverbesserer( multiverbesserer ):
    def __init__( self, verbessererlist ):
        if isinstance( verbessererlist, multiverbesserer ):
            isintruth_a_multiverbesserer = verbessererlist
            super().__init__( isintruth_a_multiverbesserer.verbessererlist )
        else:
            super().__init__( verbessererlist )

    def print_with_matplotlib( self, show = True ):
        nrows = math.ceil( math.sqrt(len( self.verbessererlist)+1) )
        nrows = max( 2, nrows )
        fig, axs = plt.subplots( nrows=nrows, ncols=nrows )
        axs =iter(itertools.chain( *axs ))
        tmpplotinfo = None
        for verbesserer in self.verbessererlist:
            tmpplotinfo = easygraph( verbesserer.oldgraph, \
                            myplotinfo = tmpplotinfo, \
                            show = False, ax = axs.__next__(), \
                            marked_nodes=["0"] )#?
        self.__plot_legend( tmpplotinfo, axs.__next__() )
        if show:
            plt.show()
        return tmpplotinfo

    def replace_in_graph_with_exception( self, mystrickgraph, markednode ):
        suc, info = self.replace_in_graph_withinfo( mystrickgraph, markednode ) 
        if not suc:
            raise StrickgraphVerbessererException( self, mystrickgraph, \
                                                            markednode )

    def __plot_legend( self, myplotinfo, axis ):
        for stitchname, mystyle in myplotinfo.stitchstyle.items():
            axis.scatter(tuple(),tuple(), label=stitchname, \
                            color = mystyle["node_color"], \
                            marker= mystyle["node_shape"] )
        axis.legend()

    def print_compare_to_graph_at_position( self, graph, marknode ):
        tmpplotinfo = self.print_with_matplotlib( show = False )
        easygraph( graph, marked_nodes =[ marknode ], \
                            myplotinfo = tmpplotinfo )

def strick_multiverbessererfromxml( xmlstr, graph_type=stricksubgraph ):
    multi = multiverbessererfromxml( xmlstr, graph_type=graph_type )
    return strick_multiverbesserer( multi )
