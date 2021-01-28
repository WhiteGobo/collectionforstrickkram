from newthing.graphtoflowcontrol import cyprogra
from newthing.graphtoflowcontrol import NODECLASS, NODEFUNCTION, EDGETYPE
from newthing.graphtoflowcontrol import nodefunctioncontainer
from .spring2dsolver import solve_gridspringgraph
import itertools
import networkx as netx
import numpy as np
from scipy.special import erfinv as function_erfinv
"""
:todo: return graph currently transforms realx to x
"""
#sqrt2 = np.sqrt(2)
MAXVALUE = np.finfo( np.float64 ).max
LENGTHDEFAULT = 0.003

class gridrelaxator():
    def __init__( self, gridgraph, surfacemap, rand, default_length=0.0 ):
        self.surfacemap = surfacemap
        #self.calcgraph = gridgraph.copy()
        self.calcgraph = netx.MultiDiGraph()
        self.calcgraph.add_nodes_from( gridgraph.nodes() )



        #expand to (surf_x, surf_y, surf_z) via *surf_xyz_tuple
        surf_xyz_tuple = self.surfacemap.singularmaps()
        surf_gradhvtoxyz_tuple = self.surfacemap.grad_realtomap()
        maxdistance_with_grad = self.surfacemap.grad_maxdistance()
        add_calculation_type_to_nodes( self.calcgraph, *surf_xyz_tuple, \
                                        *surf_gradhvtoxyz_tuple, rand, \
                                        maxdistance_with_grad )

        add_calculation_type_to_edges( self.calcgraph, \
                                            netx.Graph(gridgraph).edges(), \
                                            default_length )
        add_startposition_to_nodes( self.calcgraph, surfacemap, rand )
        self.myprogram = cyprogra( self.calcgraph )

    def relax( self, starttime = 30 ):
        for i in range( starttime ):
            self.myprogram.cycle()
            
    def get_positiongrid( self ):
        return self.insert_data_to_graph( self.calcgraph, copy=True )

    def insert_data_to_graph( self, target_gridgraph, copy=False ):
        if copy:
            target_gridgraph = target_gridgraph.copy()
        datagraph = self.myprogram.return_to_graph()
        for key in [ "x", "y", "z", "tension", "vertF" ]:
            data_to_key = netx.get_node_attributes( datagraph, key )
            netx.set_node_attributes( target_gridgraph, data_to_key, key )

        return target_gridgraph


def add_startposition_to_nodes( graph, surfacemap, rand ):
    givegraph = netx.Graph( graph )
    amin = surfacemap.xmin()
    bmin = surfacemap.ymin()
    amax = surfacemap.xmax()
    bmax = surfacemap.ymax()
    mapa_pos, mapb_pos = solve_gridspringgraph( ((amin, amax),(bmin, bmax)), \
                                                    rand, givegraph)

    if set(mapa_pos.keys()) != set(graph.nodes()):
        raise Exception("oops something went wrong")
    x_pos, y_pos, z_pos = dict(), dict(), dict()
    for node in mapa_pos:
        x, y, z = surfacemap( mapa_pos[node], mapb_pos[node] )
        x_pos.update( { node: x } )
        y_pos.update( { node: y } )
        z_pos.update( { node: z } )

    netx.set_node_attributes( graph, mapa_pos, "a" )
    netx.set_node_attributes( graph, mapb_pos, "b" )
    netx.set_node_attributes( graph, x_pos, "x" )
    netx.set_node_attributes( graph, y_pos, "y" )
    netx.set_node_attributes( graph, z_pos, "z" )


def add_calculation_type_to_nodes( graph, surf_x, surf_y, surf_z, \
                                surf_gradhx, surf_gradhy, surf_gradhz, \
                                surf_gradvx, surf_gradvy, surf_gradvz, \
                                rand, maxdelta, copy=False ):
    if copy:
        graph = graph.copy()
    node_calctype = {}
    for node in graph:
        node_calctype.update({ node: masspoint })
    for node in itertools.chain( *rand ):
        node_calctype.update({ node: staticpoint })
    netx.set_node_attributes( graph, node_calctype, NODECLASS )

    settingpairs = [ ("surfacemap_x", surf_x), ("surfacemap_y", surf_y), \
            ("surfacemap_z", surf_z), ("surf_gradhx", surf_gradhx),\
            ("surf_gradhy", surf_gradhy),("surf_gradhz", surf_gradhz),\
            ("surf_gradvx", surf_gradvx),("surf_gradvy", surf_gradvy),\
            ("surf_gradvz", surf_gradvz), ("maxdelta", maxdelta)]
    for attrname, tmpfunction in  settingpairs:
        node_func_dict = {}
        for node in graph:
            node_func_dict.update({ node: tmpfunction })
        netx.set_node_attributes( graph, node_func_dict, attrname )


    return graph

def add_calculation_type_to_edges( graph, edges, default_length, copy=False ):
    if copy:
        graph = graph.copy()

    length_attr = netx.get_edge_attributes( graph, "length" )

    for edge in edges:
        push_attr = { \
                EDGETYPE: "push", \
                "length": length_attr.get( edge, default_length ), \
                }
        graph.add_edge( edge[0], edge[1], **push_attr )

    return graph


class masspoint( nodefunctioncontainer ):
    def __init__( self, a, b, x, y, z, maxdelta, \
                        surfacemap_x, surfacemap_y, surfacemap_z,\
                        surf_gradhx, surf_gradhy, surf_gradhz, \
                        surf_gradvx, surf_gradvy, surf_gradvz,  ):
        super().__init__()
        self.save_surfacemap( surfacemap_x, surfacemap_y, surfacemap_z,\
                                surf_gradhx, surf_gradhy, surf_gradhz, \
                                surf_gradvx, surf_gradvy, surf_gradvz, \
                                surfacemap_x, surfacemap_y, surfacemap_z,\
                                )
        dampingfactor = 2.0
        self.mapa = a
        self.mapb = b
        self.x = x
        self.y = y
        self.z = z
        self.deltax = 0
        self.deltay = 0
        self.deltaz = 0
        self.tension = 0
        self.vertF = 0

        self.init_timing_graph()
        self.init_edgelibrary()

        self.x = self.surfacemap_x( self.mapa, self.mapb )
        self.y = self.surfacemap_y( self.mapa, self.mapb )
        self.z = self.surfacemap_z( self.mapa, self.mapb )
        self.save_distancerecalc( maxdelta, dampingfactor )

    def save_distancerecalc( self, maxdistance, dampingfactor ):
        if dampingfactor < 1:
            raise Exception("Damping factor cant be lower than 1")
        if dampingfactor < maxdistance:
            maxx = MAXVALUE
            maxy = MAXVALUE * (dampingfactor / maxdistance)
        else:
            maxx = MAXVALUE / (dampingfactor / maxdistance )
            maxy = MAXVALUE
        self.distancerecalc_x = ( 0, \
                            maxdistance/dampingfactor, \
                            maxx )
        self.distancerecalc_y = ( 1, \
                            dampingfactor, \
                            maxy )


    def save_surfacemap( self, surfacemap_x, surfacemap_y, surfacemap_z,\
                            surf_gradhx, surf_gradhy, surf_gradhz, \
                            surf_gradvx, surf_gradvy, surf_gradvz, \
                            nx, ny, nz ):
        self.surfacemap_x = surfacemap_x
        self.surfacemap_y = surfacemap_y
        self.surfacemap_z = surfacemap_z
        self.surfacemap_gradhx = surf_gradhx
        self.surfacemap_gradhy = surf_gradhy
        self.surfacemap_gradhz = surf_gradhz
        self.surfacemap_gradvx = surf_gradvx
        self.surfacemap_gradvy = surf_gradvy
        self.surfacemap_gradvz = surf_gradvz
        self.nx, self.ny, self.nz = nx, ny, nz


    def init_timing_graph( self ):
        resetattr = {NODEFUNCTION: self.resetposition}
        self.timing_graph.add_node( "resetposition", **resetattr )
        moveattr = {NODEFUNCTION: self.move}
        self.timing_graph.add_node( "move", **moveattr )

        self.timing_graph.add_edge( "resetposition", "move" )


    def init_edgelibrary( self ):
        edgetype = "push"
        push_after = ["resetposition"]
        push_before = ["move"]
        #gespraech_after_other = ["resetposition"]
        #gespraech_before_other = ["move"]
        self.add_possible_edge_to( masspoint, edgetype, self.push,\
                            push_after, push_before, push_after,push_before )
        self.add_possible_edge_to( staticpoint, edgetype, self.push,\
                            push_after, push_before, push_after,push_before )


    def resetposition( self ):
        self.deltax = 0
        self.deltay = 0
        self.deltaz = 0
        self.tension = 0
        #self.x = self.surfacemap_x( self.mapa, self.mapb )
        #self.y = self.surfacemap_y( self.mapa, self.mapb )
        #self.z = self.surfacemap_z( self.mapa, self.mapb )


    def move( self ):
        gradhx = self.surfacemap_gradhx( self.mapa, self.mapb )
        gradhy = self.surfacemap_gradhy( self.mapa, self.mapb )
        gradhz = self.surfacemap_gradhz( self.mapa, self.mapb )
        gradvx = self.surfacemap_gradvx( self.mapa, self.mapb )
        gradvy = self.surfacemap_gradvy( self.mapa, self.mapb )
        gradvz = self.surfacemap_gradvz( self.mapa, self.mapb )
        vert_Fx = self.nx( self.mapa, self.mapb )
        vert_Fy = self.ny( self.mapa, self.mapb )
        vert_Fz = self.nz( self.mapa, self.mapb )

        db, da, vertF = np.dot( ((gradhx, gradhy, gradhz),\
                                    (gradvx, gradvy, gradvz),\
                                    (vert_Fx, vert_Fy, vert_Fz )),\
                                    (self.deltax, self.deltay, self.deltaz) )
        
        tmp = np.linalg.norm(( da, db ))

        tmp = np.interp( tmp, self.distancerecalc_x, self.distancerecalc_y )
        self.mapa = self.mapa + da/tmp
        self.mapb = self.mapb + db/tmp

        self.x = self.surfacemap_x( self.mapa, self.mapb )
        self.y = self.surfacemap_y( self.mapa, self.mapb )
        self.z = self.surfacemap_z( self.mapa, self.mapb )

        self.vertF = vertF


    def push( self, other, length ):
        length = LENGTHDEFAULT
        dx = other.x - self.x
        dy = other.y - self.y
        dz = other.z - self.z
        tmplen = np.linalg.norm(( dx, dy, dz ))
        invtmplen = 1/np.interp( tmplen, (0,0.0001,MAXVALUE),\
                                        (0.0001,0.0001,MAXVALUE))
        self.deltax = self.deltax + dx*invtmplen * (tmplen - length)
        self.deltay = self.deltay + dy*invtmplen * (tmplen - length)
        self.deltaz = self.deltaz + dz*invtmplen * (tmplen - length)
        other.deltax = other.deltax - dx*invtmplen * (tmplen - length)
        other.deltay = other.deltay - dy*invtmplen * (tmplen - length)
        other.deltaz = other.deltaz - dz*invtmplen * (tmplen - length)
        self.tension = self.tension + ( tmplen-length )**2
        other.tension = self.tension + ( tmplen-length )**2

class staticpoint( nodefunctioncontainer ):
    def __init__( self, a, b, x, y, z, \
                        surfacemap_x, surfacemap_y, surfacemap_z,\
                        surf_gradhx, surf_gradhy, surf_gradhz, \
                        surf_gradvx, surf_gradvy, surf_gradvz,  ):
        super().__init__()
        self.save_surfacemap( surfacemap_x, surfacemap_y, surfacemap_z,\
                                surf_gradhx, surf_gradhy, surf_gradhz, \
                                surf_gradvx, surf_gradvy, surf_gradvz )
        self.maxdistance = 0.1
        self.mapa = a
        self.mapb = b
        self.x = x
        self.y = y
        self.z = z
        self.deltax = 0
        self.deltay = 0
        self.deltaz = 0
        self.tension = 0
        self.vertF = 0

        self.init_timing_graph()
        self.init_edgelibrary()


    def save_surfacemap( self, surfacemap_x, surfacemap_y, surfacemap_z,\
                            surf_gradhx, surf_gradhy, surf_gradhz, \
                            surf_gradvx, surf_gradvy, surf_gradvz,  ):
        self.surfacemap_x = surfacemap_x
        self.surfacemap_y = surfacemap_y
        self.surfacemap_z = surfacemap_z
        self.surfacemap_gradhx = surf_gradhx
        self.surfacemap_gradhy = surf_gradhy
        self.surfacemap_gradhz = surf_gradhz
        self.surfacemap_gradvx = surf_gradvx
        self.surfacemap_gradvy = surf_gradvy
        self.surfacemap_gradvz = surf_gradvz


    def init_timing_graph( self ):
        resetattr = {NODEFUNCTION: self.resetposition}
        self.timing_graph.add_node( "resetposition", **resetattr )
        moveattr = {NODEFUNCTION: self.move}
        self.timing_graph.add_node( "move", **moveattr )

        self.timing_graph.add_edge( "resetposition", "move" )


    def init_edgelibrary( self ):
        edgetype = "push"
        push_after = ["resetposition"]
        push_before = ["move"]
        #gespraech_after_other = ["resetposition"]
        #gespraech_before_other = ["move"]
        self.add_possible_edge_to( masspoint, edgetype, self.push,\
                            push_after, push_before, push_after,push_before )

        self.add_possible_edge_to( staticpoint, edgetype, self.nopush,\
                            push_after, push_before, push_after,push_before )


    def resetposition( self ):
        return

    def move( self ):
        return

    def push( self, other, length ):
        length = LENGTHDEFAULT
        dx = other.x - self.x
        dy = other.y - self.y
        dz = other.z - self.z
        tmplen = np.linalg.norm(( dx, dy, dz ))
        invtmplen = 1/np.interp( tmplen, (0,0.0001,MAXVALUE),\
                                        (0.0001,0.0001,MAXVALUE))
        other.deltax = other.deltax - dx*invtmplen * (tmplen - length)
        other.deltay = other.deltay - dy*invtmplen * (tmplen - length)
        other.deltaz = other.deltaz - dz*invtmplen * (tmplen - length)

        other.tension = self.tension + ( tmplen-length )**2


    def nopush( self, other ):
        return
