import networkx as _netx
import numpy as np
from scipy.sparse.linalg import spsolve as solve
import networkxarithmetic as arit
import networkx as netx
#import numba

class InstabilityError( Exception ):
    pass

class gridrelaxator():
    def __init__( self, gridgraph, surfacemap, rand, strengthmultiplier = 1.0,\
                            numba_support=False):
        """
        gives every node a calculationtype
        :todo: replace knotdistance and knotstrength with edgeattribute 
                in gridgraph
        :param gridgraph: 
        :type gridgraph: networkx.Graph
        :type surfacemap: map 2D to 3D
        :type rand: nested list len==4
        :param rand: list of the borders (down, left, right, up)
                    elements in borders must correspond to node in gridgraph
        :param timestep: decrease if gridrelaxation is instable
        """
        if numba_support:
            raise Exception("numba currently not supported")
        self.numba_support = numba_support
        self.strengthmultiplier = [strengthmultiplier]
        self.cycle_functions = None
        self.gridgraph = netx.MultiDiGraph( gridgraph )
        self.surfacemap = surfacemap
        
        # i will instead use a static array to work within move-cmd of spring
        #self.gridgraph = self.use_strengthmultiplier( strengthmultiplier, \
        #                                                self.gridgraph )
        self.gridgraph = self._set_randposition( rand, self.gridgraph )
        self.gridgraph = self._set_innerstartingposition( rand, self.gridgraph )

        edgeattr = { x:"push" for x in self.gridgraph.edges( keys=True ) }
        netx.set_edge_attributes( self.gridgraph, edgeattr, "edgetype" )

        self.gridgraph = self.insert_spannungsmesser( self.gridgraph )

        #self.gridgraph.clear_edges()
        self.graphcode = self._create_cycle_functions( self.gridgraph )

    def insert_spannungsmesser( self, gridgraph ):
        othernodes = list( gridgraph.nodes() )
        gridgraph.add_node( "spannungsmesser", calctype="spannungsmesser" )
        for node in othernodes:
            gridgraph.add_edge( node, "spannungsmesser", \
                                    edgetype="spannung_push")

        return gridgraph

    def use_strengthmultiplier( self, strengthmultiplier, gridgraph ):
        strengthlib = netx.get_edge_attributes( gridgraph, "strength" )
        strengthlib = { x:strengthlib[x]*strengthmultiplier \
                        for x in strengthlib }
        netx.set_edge_attributes( gridgraph, strengthlib, "strength" )
        return gridgraph

    def get_positiongrid( self ):
        """
        return the position of all nodes of the grid
        """
        datagraph = self.graphcode.transferdatatograph()
        x = netx.get_node_attributes( datagraph, "xreal" )
        y = netx.get_node_attributes( datagraph, "yreal" )
        z = netx.get_node_attributes( datagraph, "zreal" )

        returngraph = netx.Graph()
        returngraph.add_nodes_from( datagraph.nodes() )
        netx.set_node_attributes( returngraph, x, "x" )
        netx.set_node_attributes( returngraph, y, "y" )
        netx.set_node_attributes( returngraph, z, "z" )
        returngraph.add_edges_from( self.gridgraph.edges() )
        edgelength = {}
        tension = {}
        returngraph.remove_node( "spannungsmesser" )
        for tmpedge in returngraph.edges():
            deltax = x[ tmpedge[0] ] - x[ tmpedge[1] ]
            deltay = y[ tmpedge[0] ] - y[ tmpedge[1] ]
            deltaz = z[ tmpedge[0] ] - z[ tmpedge[1] ]
            edgelength.update({ tmpedge: \
                                np.linalg.norm([deltax, deltay, deltaz])  })
            tension.update({ tmpedge: \
                        np.abs(0.1 - np.linalg.norm([deltax, deltay, deltaz]))})
        netx.set_edge_attributes( returngraph, edgelength, "currentlength" )
        netx.set_edge_attributes( returngraph, tension, "tension" )

        
        return returngraph

    def relax( self, maximal_error, testtime = 10, test_arraylength = 4, \
                                    starttime=100 ):
        """
        cycle till spannung is in estimatly equilibrium
        :param maximal_error: the maximal difference between the equilibrium
                            tension and the current tension.
                            the strengthmultiplier will be compensated
        :type maximal_error: float
        :param testtime: do this many cycles before testing if 
                        graph is as relaxed as it can be
        :type testtime: int
        """

        for i in range( starttime ):
            self._cycle()
        return
        measurepoints = []
        for i in range( test_arraylength ):
            self._cycle()
            measurepoints.append( self.graphcode.values[ \
                    self.graphcode.dataname_list.index(\
                        "spannungsmesser"+"spannungsum") \
                    ])
        estimated_error, valid_estimation = \
            self.spannungserror_estimation( measurepoints, test_arraylength )
        while np.abs(estimated_error) > maximal_error:
            self._cycle()
            measurepoints.pop( 0 )
            measurepoints.append( self.graphcode.values[ \
                    self.graphcode.dataname_list.index(\
                        "spannungsmesser"+"spannungsum") \
                    ])
            estimated_error, valid_estimation = \
                self.spannungserror_estimation( measurepoints, test_arraylength)
            if valid_estimation > 100*np.abs(estimated_error):
                print("asd")
                self.strengthmultiplier[0] =self.strengthmultiplier[0] * 0.7

        return

        for i in range( int(5e2) ):
            print("asd")
            self._cycle()
        return
        # for stability the strengthmult is set, so the tension is lowered by
        # its amount. this calculation compensates for this:
        maximal_error = maximal_error * self.strengthmultiplier

        measurepoints = []
        for i in range( test_arraylength ):
            self._cycle()
            measurepoints.append( self.graphcode.values[ \
                    self.graphcode.dataname_list.index(\
                        "spannungsmesser"+"spannungsum") \
                    ])
        estimated_error, valid_estimation = \
            self.spannungserror_estimation( measurepoints, test_arraylength )
        if measurepoints[-1] > measurepoints[-2] or estimated_error < 0:
            raise InstabilityError( "grid is not relaxing anymore" )
        while estimated_error > maximal_error \
                                    or valid_estimation > maximal_error:
            self._cycle()
            measurepoints.pop( 0 )
            measurepoints.append( self.graphcode.values[ \
                    self.graphcode.dataname_list.index(\
                        "spannungsmesser"+"spannungsum") \
                    ])
            estimated_error, valid_estimation = \
                self.spannungserror_estimation( measurepoints, test_arraylength)
            if measurepoints[-1] > measurepoints[-2] or estimated_error < 0:
                raise InstabilityError( "grid is not relaxing anymore" )

    def spannungserror_estimation( self, measurepoints, test_arraylength ):
        """
        Estimates the distance of a exponentailfunction to its equilibrium
        """
        fitvalues = np.array( measurepoints )
        tvalues = np.exp( np.arange( len(measurepoints)))
        coefficients, residuals, rank, sing_values, cond_threshold = \
                    np.polyfit( tvalues, fitvalues, 1, full=True )
        fiterror = np.abs( residuals[0] / len(measurepoints) )
        # -1 == test_arraylength-1
        distance_to_equilibrium = (measurepoints[-1] - measurepoints[0]) \
                                /(1- (tvalues[-1] * coefficients[1]))
        return distance_to_equilibrium, fiterror

            

    def _cycle( self ):
        for i in range( 10 ):
            self.graphcode.cycle()


    def _create_cycle_functions( self, gridgraph ):

        code_library, edge_library = self._create_node_and_edge_libraries()

        graphcode = arit.graphcontainer()
        graphcode.update_calclibrary( code_library )
        graphcode.update_edgelibrary( edge_library )
        graphcode.createcode_with_graph( gridgraph, \
                                        numba_support=self.numba_support )

        return graphcode

    def _create_node_and_edge_libraries( self ):
        code_library = {}
        surfmapx, surfmapy, surfmapz = self.surfacemap.singularmaps()
        springcyclefunction = springnode_cycle_withmap( surfmapx, surfmapy, \
                                            surfmapz, self.strengthmultiplier )
        code_library.update( {"spring": springcyclefunction } )
        code_library.update( {"constantposition": constantnode_code } )
        code_library.update( {"spannungsmesser": spannungsmesser_code } )

        edge_library = {("spring", "spring","push"):springtospring_push,
                ("constantposition", "spring","push"):consttospring_push,
                ("spring", "constantposition","push"):constanttoconstant_push,
                ("constantposition", "constantposition","push"):\
                                        constanttoconstant_push,
                ("spring", "spannungsmesser", "spannung_push"):\
                                        springtospannungsmesser_push,
                ("constantposition", "spannungsmesser", "spannung_push"):\
                                        constanttospannungsmesser_push,
                }

        return code_library, edge_library

    def _set_innerstartingposition( self, rand, calcgraph ):
        innernodes = set(calcgraph.nodes()) \
                    - set(rand[0]+rand[1]+rand[2]+rand[3])

        nodetypes = { x:"spring" for x in innernodes }
        netx.set_node_attributes( calcgraph, nodetypes, "calctype" )

        nodevalues = self._calculate_initialposition( innernodes,\
                                                rand[0]+rand[1]+rand[2]+rand[3])

        for i in range(5):
            tmp_nodeattr = ["xmap", "ymap", "xreal", "yreal", "zreal"][ i ]
            tmpdict = { node:nodevalues[node][ i ] for node in nodevalues }
            netx.set_node_attributes( calcgraph, tmpdict, tmp_nodeattr )
        return calcgraph

    def _calculate_initialposition( self, innernodes, rand ):
        """
        _set_randposition must be called
        solves simple spring equations for the gridgraph. rand will be set as
        constant positions. for restnodes the equation is:
            einstein-sum-convention
            for a,b,weight in edges_to_a: a.x*weight = b.x*weight
        :todo: rand and randnodes doing the same thing, remove duplicate
        """
        nodetypes = netx.get_node_attributes( self.gridgraph, "calctype" )
        nodex = netx.get_node_attributes( self.gridgraph, "xmap" )
        nodey = netx.get_node_attributes( self.gridgraph, "ymap" )
        randnodes = [ node for node in nodetypes \
                        if nodetypes[node]=="constantposition"]
        randpositiondict = { node:( nodex[node], nodey[node] ) \
                            for node in randnodes }
        nodemappositions = _springgrid2d_relaxation( self.gridgraph, \
                                                    randpositiondict)
        nodevalues = {}
        for node in innernodes:
            xmap = nodemappositions[ node ][0]
            ymap = nodemappositions[ node ][1]
            xreal,yreal,zreal = self.surfacemap( xmap, ymap )
            nodevalues.update({ node:( xmap, ymap, xreal, yreal, zreal ) })
        return nodevalues

    def _set_randposition( self, rand, calcgraph ):
        """
        sets border position with euidistants nodes
        """
        (down, up, left, right) = rand #mass assignment
        xmin = self.surfacemap.xmin()
        ymin = self.surfacemap.ymin()
        xmax = self.surfacemap.xmax()
        ymax = self.surfacemap.ymax()

        nodetypes = { x:"constantposition" for x in up+down+left+right }
        netx.set_node_attributes( calcgraph, nodetypes, "calctype" )

        nodevalues = {}
        for tmpnode in down:
            i = down.index( tmpnode )
            xmap = xmin + (xmax-xmin)*(i/(len(down)-1)) #ranges from 0 to 1
            xreal,yreal,zreal = self.surfacemap( xmap, ymin )
            nodevalues.update( {tmpnode:( xmap, ymin, xreal,yreal,zreal )} )
        for tmpnode in up:
            i = up.index( tmpnode )
            xmap = xmin + (xmax-xmin)*(i/(len(up)-1)) #ranges from 0 to 1
            xreal,yreal,zreal = self.surfacemap( xmap, ymax )
            nodevalues.update( {tmpnode:( xmap, ymax, xreal,yreal,zreal )} )
        for tmpnode in left:
            i = left.index( tmpnode )
            ymap = ymin + (ymax-ymin)*(i/(len(left)-1)) #ranges from 0 to 1
            xreal,yreal,zreal = self.surfacemap( xmin, ymap )
            nodevalues.update( {tmpnode:( xmin, ymap, xreal,yreal,zreal )} )
        for tmpnode in right:
            i = right.index( tmpnode )
            ymap = ymin + (ymax-ymin)*(i/(len(right)-1)) #ranges from 0 to 1
            xreal,yreal,zreal = self.surfacemap( xmax, ymap )
            nodevalues.update( {tmpnode:( xmap, ymap, xreal,yreal,zreal )} )
        for i in range(5):
            tmp_nodeattr = ["xmap", "ymap", "xreal", "yreal", "zreal"][ i ]
            tmpdict = { node:nodevalues[node][ i ] for node in nodevalues }
            netx.set_node_attributes( calcgraph, tmpdict, tmp_nodeattr )

        return calcgraph



def _springgrid2d_relaxation( graph, constantposition_dict ):
    """
    relaxate a grid of points connected by spring on a PLANAR surface
    This method is used to give a starting value of the position of all the
    points on the abbildung of 3d surface to a planar surface
    :type graph: networkx.Graph; freezed
    :type constantposition_dict: dictionary
    :param constantposition_dict: assign partially the nodes of graph a position
                    example: const_dict[ example_node ] = (x,y)
    """
    order_nodes = list( graph.nodes() )
    x_sol, y_sol = _springgrid2d_createsolutionvector( graph, \
                                    constantposition_dict, order_nodes )

    adj_sparsematrix = _springgrid2d_equationmatrix( graph, \
                                    constantposition_dict, order_nodes )

    x_solved = solve( adj_sparsematrix, x_sol )
    y_solved = solve( adj_sparsematrix, y_sol )
    
    nodepositions = {}
    for i in range( len(order_nodes) ):
        nodepositions.update({order_nodes[i]:( x_solved[i], y_solved[i] )})
    return nodepositions


def _springgrid2d_equationmatrix( graph, position, orderedlist ):
    """
    sets matrix for equation equal to:
        einstein-sum-convention
        for a,b,weight in edges_to_a: a.x*weight = b.x*weight
    :type graph: networkx.Graph
    :type positions: dictionary
    :type orderedlist: list
    :param positions: assign partially the nodes of graph a position
                    example: const_dict[ example_node ] = (x,y)
    :param orderedlist: list equal to graph.nodes(). gives an order for nodes
    """
    #create interaction equation for every node
    adj_sparsematrix = netx.linalg.adjacency_matrix( graph, orderedlist )
    adj_lilmatrix = adj_sparsematrix.tolil()
    for i in  range( len( orderedlist ) ):
        tmpnode = orderedlist[i]
        adj_lilmatrix[ i,i ] = -1 * len( list(graph.neighbors( tmpnode )))

    #sets equation to constant for specific rows(j) 
    #   matrix[i][j] = (if i==j: =1; else: =0)
    for tmpnode in position:
        i = orderedlist.index( tmpnode )
        for j in range( len( orderedlist )):
            adj_lilmatrix[ i, j ] = 0
        adj_lilmatrix[ i,i ] = 1
    return type(adj_sparsematrix)( adj_lilmatrix )


def _springgrid2d_createsolutionvector( graph, positions, orderedlist ):
    """
    For all the node inside the grid all springforces must sum up to 0.
    for all the edgepoints the solution is the same as the solutionvector, that 
    is created here.
    :type graph: networkx.Graph
    :type positions: dictionary
    :type orderedlist: list
    :param positions: assign partially the nodes of graph a position
                    example: const_dict[ example_node ] = (x,y)
    :param orderedlist: list equal to graph.nodes(). gives an order for nodes
    """
    x_vector = np.zeros( len(orderedlist) )
    y_vector = np.zeros( len(orderedlist) )
    for node in positions:
        index = orderedlist.index( node )
        x_vector[ index ] = positions[ node ][0]
        y_vector[ index ] = positions[ node ][1]
    return x_vector, y_vector

def springnode_cycle_withmap( mymap_x, mymap_y, mymap_z, strengthmult_pointer ):
    """
    creates a function for use in graphcode; see decorator for help
    :type strengthmult_pointer: list
    :param strengthmult_pointer: a pointer to the strengthmult variable to set
                    the progression-speed of the simulation
    """
    def springnode_cycle():
        data_dict = { "xmap":None, "ymap":None, "xreal":None, "yreal":None, \
                    "zreal":None, "deltaxmap":0, "deltaymap":0, "spannung":0 }
        code_graph =  netx.DiGraph()
        code_graph.add_node( "reset", \
                code=["%s = 0", "%s = 0", "%s = 0"], \
                values=[("deltaxmap",),("deltaymap",),("spannung",)])
        code_graph.add_node( "move", \
                    code=["%s =%s + %s", \
                        "%s = %s + %s"], \
                                        values=[("xmap","xmap","deltaxmap"),\
                                            ("ymap", "ymap", "deltaymap")])
        transcode=["%s = transx( %s, %s )",\
                    "%s = transy( %s, %s )",\
                    "%s = transz( %s, %s )"]
        transvalue=[("xreal","xmap","ymap"),("yreal","xmap","ymap"),\
                    ("zreal","xmap","ymap")]

        translatepos_x = mymap_x
        translatepos_y = mymap_y
        translatepos_z = mymap_z

        code_graph.add_node( "translateposition", code=transcode, \
                            values=transvalue)
        code_graph.add_edge( "reset", "move" )
        code_graph.add_edge( "translateposition", "reset" )
        functiondictionary = { "transx":translatepos_x, \
                            "transy":translatepos_y, "transz":translatepos_z }

        return data_dict, code_graph, functiondictionary
    return springnode_cycle


def constantnode_code():
    data_dict = { "xmap":None, "ymap":None, "xreal":None, "yreal":None, \
                "zreal":None,  }
    code_graph =  netx.DiGraph()
    return data_dict, code_graph, {}

def spannungsmesser_code():
    data_dict = { "spannungsum":0 }
    code_graph = netx.DiGraph()
    code_graph.add_node( "reset", code=["%s=0.0"], \
                            values=[("spannungsum",)])
    return data_dict, code_graph, {}


def constanttospannungsmesser_push():
    code_graph = netx.DiGraph()
    return code_graph, [], [], [], [], {}

def springtospannungsmesser_push():
    after_exec_out = ["move"]
    after_exec_in = ["reset"]
    before_exec_out = []
    before_exec_in = []
    code_graph = netx.DiGraph()
    mycode = ["%s = %s + %s"]
    myvalues = [(("in","spannungsum"),("in","spannungsum"),\
                    ("out","spannung"))]
    code_graph.add_node( "tester", code=mycode, values=myvalues )
    return code_graph, after_exec_out, after_exec_in, \
                        before_exec_out, before_exec_in, {}

def constanttoconstant_push( length, strength ):
    code_graph = netx.DiGraph()
    return code_graph, [], [], [], [], {}

def springtospring_push( length, strength ):
    after_exec_out = ["reset"]
    after_exec_in = ["reset"]
    before_exec_out = ["move"]
    before_exec_in = ["move"]
    code_graph = netx.DiGraph()
    mycode = ["tmpdeltaxmap = %s -%s", #1
            "tmpdeltaymap = %s -%s",
            "tmpnorm = np.linalg.norm(np.array([tmpdeltaxmap, tmpdeltaymap]))",
            "tmpspannung = getspannung( %s, %s, %s, %s, %s, %s, "\
                                        + " %f, %f )" % (length, strength),
            "%s = %s + tmpdeltaxmap * tmpspannung / tmpnorm", #8
            "%s = %s + tmpdeltaymap * tmpspannung / tmpnorm",
            "%s = %s + np.abs(tmpspannung)" #10
            ]
    myvalues=[(("in", "xmap"), ("source", "xmap")), #1
            (("in", "ymap"), ("out", "ymap")),
            tuple(),
            (("in","xreal"),("in","yreal"),("in","zreal"),("out","xreal"),("out","yreal"),("out","zreal")),
            (("in", "deltaxmap"),("in", "deltaxmap")), #8
            (("in", "deltaymap"),("in", "deltaymap")),
            (("in", "spannung"),("in", "spannung"))
            ]
    code_graph.add_node( "push", code=mycode, values=myvalues )
    return code_graph, after_exec_out, after_exec_in, \
                        before_exec_out, before_exec_in, {"getspannung":consttospring_push_func1}

#@numba.njit
def consttospring_push_func1( targ_xreal, targ_yreal, targ_zreal, \
                        source_xreal, source_yreal, source_zreal, \
                        length, strength,
                        ):
    deltax = targ_xreal - source_xreal
    deltay = targ_yreal - source_yreal
    deltaz = targ_zreal - source_zreal
    tmpspannung = strength \
                *(length - np.linalg.norm( np.array([deltax, deltay, deltaz])))
    return tmpspannung
    

def consttospring_push( length, strength ):
    after_exec_out = []
    after_exec_in = ["reset"]
    before_exec_out = []
    before_exec_in = ["move"]

    code_graph = netx.DiGraph()
    mycode = ["tmpdeltaxmap = %s -%s", #1
            "tmpdeltaymap = %s -%s",
            "tmpnorm = np.linalg.norm(np.array([tmpdeltaxmap, tmpdeltaymap]))",
            "tmpspannung = getspannung( %s, %s, %s, %s, %s, %s, "\
                                        + " %f, %f )" % (length, strength),
            "%s = %s + tmpdeltaxmap * tmpspannung / tmpnorm", #8
            "%s = %s + tmpdeltaymap * tmpspannung / tmpnorm",
            "%s = %s + np.abs(tmpspannung)", #10
            ]
    myvalues=[(("in", "xmap"), ("source", "xmap")), #1
            (("in", "ymap"), ("out", "ymap")),
            tuple(),
            (("in","xreal"),("in","yreal"),("in","zreal"),("out","xreal"),("out","yreal"),("out","zreal")),
            (("target", "deltaxmap"),("target", "deltaxmap")), #8
            (("in", "deltaymap"),("in", "deltaymap")),
            (("in", "spannung"),("in", "spannung")),
            ]
    code_graph.add_node( "push", code=mycode, values=myvalues )
    return code_graph, after_exec_out, after_exec_in, \
                before_exec_out, before_exec_in, {"getspannung":consttospring_push_func1}
