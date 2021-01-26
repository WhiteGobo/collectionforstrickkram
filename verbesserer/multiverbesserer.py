from extrasfornetworkx import multiverbesserer
from extrasfornetworkx import multiverbessererfromxml
from ..strickgraph.strickgraph_base import stricksubgraph
import itertools
import math

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
        plt.figure()
        nrows = math.ceil( math.sqrt(len( self.verbessererlist)) )
        nrows = max( 2, nrows )
        fig, axs = plt.subplots( nrows=nrows, ncols=nrows )
        i = 0
        axs =list(itertools.chain( *axs ))
        for verbesserer in self.verbessererlist:
            easygraph( verbesserer.oldgraph, show = False, ax = axs[i], \
                            marked_nodes=["0"] )#?
            i=i+1
        if show:
            plt.show()

    def print_compare_to_graph_at_position( self, graph, marknode ):
        self.print_with_matplotlib( show = False )
        easygraph( graph, marked_nodes =[ marknode ] )

def strick_multiverbessererfromxml( xmlstr, graph_type=stricksubgraph ):
    multi = multiverbessererfromxml( xmlstr, graph_type=graph_type )
    return strick_multiverbesserer( multi )
