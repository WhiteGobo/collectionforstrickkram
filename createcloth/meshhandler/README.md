# Physic
## nomenclatur
Read this if you feel buffled by my misuse of physical terms:)

I will freely swap between the use of particle and stitch. They both mean
the same.

The distance will be used as relative vector between two positions.

I dont intend to give information about constants, other then how they are used.

## Problems in finding the equilibrium. Why numerical solution?
All the stitchtes are bind to the surface of a body. So in order to find a solution, you need not an free physic simulation, but something that binds the 
stitches to the surface. In order to achive this i will save the 3D-surface
as 2D-Map( see eg Kohonen ) and save all the information of the stitches in 2D.
real-position = Map( map-position )

See create_surfacemap.py for more information

## hookes law - formulas
The goal is to have every stitch in an equilibrium.
For that we need a motion formula(a=f(?)) (and all formulas for its variables).
With this we can formulate a method to get to an equilibrium state, where no 
motion is.


Motion Formula, acceleration:
The acceleration $a/m$ of each stitch $i$ is described via all forces $F$ 
between itself an all its neighbours $j$:

$a_i/m_i = \sum_j F_i^j$

We abbreviate the mass $m_i$ away because it is irrelevant in equilibrium:

$a_i = \sum_j F_i^j$

Note: newtons law
The Force $F_i^j$ acting on particle $i$ from particle $j$ also acts on $j$:

$F_i^j = -F_j^i$

Force formula, hookes law, spring force:
The Force between particle $i$ and particle $j$ is described via 
their distance $\vec{d}_i^j $, the springconstant $k_{(i,j,n)}$, and 
the nominal length $D_{ijn}$ of each connection $ijn$:
abbreviation for distance $d = \vec{d}_i^j$:

$F_i^j = -k_{ijn} (d/|d|) *(|d| -D_{ijn} )$

The Distance $\vec(d)_i^j $ is in this program always a vector. it is described
by the real position $(x_i, y_i, z_i)$ of the two particles $i$ and $j$:

$\vec(d)_i^j = (x_i-x_j, y_i -y_i, z_i-z_j)$

Between all nodepairs $ij$ there are $N_{ij}$ connections. Each connection 
will be referred to via its index $n<N_{ij}$. So the possible ids for connections between $i$ and $j$ are:

$ij0, ij1, ..., ij(N_{ij}-1)$

For each of these connections there are two constants:
constants for $ijn$: nominal length D_{ijn}, spring constant $k_{ijn}$

## Finding the equilibrium, formulas
The idea is to minimize the energy in the system.
So for every step: $E_k+1 < E_k$

$E_k = \sum_i \sum_j \frac12 (F_i^j)**2$

The Force $F_i^j$ depend on the step $k$ because the positions are 
different each step.

Also we dont alterate the real position $x,y,z$ directly. We alterate 
the map position of each stitch $x_m, y_m$ which is translated to the real
position.
Because of this need a translation tensor between real space and map space or rather an translation tensor between motion of the real space and the map space.

$T \Delta p_real = \Delta p_map$

With the relaxation algorithm we move the particles in real space. And to get 
the next position we translate this movement to a movement in map space and
apply the movement on the map position of each stitch

todo: Explanation on how the algortihm functions

## mapping thingies
You need to supply a surface map for the program. 
(see: program thingis>surface map)
This surface map will be conversed via kohonen algorithm towards 2d map.
The algorithm is a little bit alterated by me.
First the border of the surface map will be identified. This border will be forced as border for the kohonen map.

Every else is exactly as it should be in kohnen maps, so please find 
additional information yourself.


Also for every map tile there should be a tensor $T$ given which converts 
a small motion in real space to a forced motion on the surface in the map space:

$T \Delta (x,y,z) = \Delta(x_m, y_m)$

$T = ((xx, xy),(yx, yy),(zx, zy))$

eg: $zx$ is contribution of real $z$ motion to the mapped $x$ motion.

For the mathematics i use please see create_surfacemap.py
I plan on explain it here, but after im firm on how this program should work:)

## pseudo inverse ( penrose-moore matrix )
Through the mapping function i only get the correlation from x_m,y_m to x,y,z. 
Which is only naturla, because you cant map the whole 3d-world onto the map.
To get the differential $dx_m/dx$ we use a pseudo invert matrix, which maps 
the normal vector to a zero vector.
See numpy.linalg.pinv

calculation is as follows:

get $grad(x,y,z)[a,b]$

$grad(a,b)[x,y,z] = pseudoinvert( grad(x,y,z)[a,b] )$

to get the movement in mappingspace from $Dx, Dy, Dz$:

$Da, Db = grad(a,b)[x,y,z] * Dx, Dy, Dz$

# program thingis
##  surface map
>Wow you were sent here??
>>Ha, good luck my friend:P

