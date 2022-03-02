Stitchinfo
==========

Description
-----------

The knitcharts as described in :ref:`Strickgraph` consist of different
stitchtypes. You can also describe knitpieces via patterns.

Stitchtypes
-----------

Stitchtypes normally are only needed, so that the knitter know, what he should
do, from row to row. 

But computer need some more information over the stitchtype, to be able to
handle it. Dependend on the stitchtypes used in a line, the line needs a 
different number of stitches. E.g. instead of 2 knit-stitches you can use 1 k2tog-stitch. But in the nextline 1 stitch less can be used.

For this reason every stitchtype have a corresponding number of upedges 
and downedges.

So to declare a stitchtype following information is needed:
        * a unique name
        * a symbol for knitcharts
        * number of upedges
        * number of downedges

See for example a declaration of a stitchtype in 
:data:`createcloth.stitchinfo.stitches.xml`:

.. code::

	<stitchtype name="knit"
		manualchar="k"
		upedges="1"
		downedges="1"
	/>

Comment on stitchcharts
-----------------------

Currently in manuals there are some special commands like tunnel and load. 
These special commands should be explained further in the chapter with 
manual-strickgraph-thingies.

.. todo:

   make somekind of chapter for special commands anywhere and link it here

These special commands may be implemented in stitchinfo in the future.

python-implementation of stitchdata
-----------------------------------

For a unified way of handling all stitchtype-data in python, the class
:py:class:`stitchcontainer<createcloth.stitchinfo.load_stitchinfo.stitchdatacontainer>`
is introduced.

The available stitchtypes(names) and their symbol can be accesed via 
:py:data:`stitchsymbol<createcloth.stitchinfo.load_stitchinfo.stitchdatacontainer.stitchsymbol>`.
For access to the number of upedges and downedges the variables upedges 
and downedges are provided. Eg:

.. code::

   from createcloth.stitchinfo import basic_stitchdata
   from createcloth.stitchinfo import stitchdatacontainer
   basic_stitchdata: stitchdatacontainer

   all_stitchtypes = basic_stitchdata.stitchsymbol.keys()
   # [ "knit", "yarnover", "bindoff", ... ]

   knit_symbol    = basic_stitchdata.stitchsymbol[ "knit" ]
   knit_upedges   = basic_stitchdata.upedges[ "knit" ]
   knit_downedges = basic_stitchdata.downedges[ "knit" ]
   # knit_symbol, knit_upedges, knit_upedges = "k", 1, 1

The stitchtypes can have also an influence on physicsimulation, but this
is something i want to discuss in more detail in
:py:mod:`createcloth.physicalhelper`.

Maybe something about strickdata??
----------------------------------

i wanted in the same file, as stitchtypes are declared als declare 
knittingpatterns. Currently they are called strickdata inside the xmlfile.

They are accessed via
:py:data:`stitchdatacontainer.strickstitch<createcloth.stitchinfo.load_stitchinfo.stitchdatacontainer.strickstitch>`, 
:py:data:`stitchdatacontainer.strickstart<createcloth.stitchinfo.load_stitchinfo.stitchdatacontainer.strickstart>` and
:py:data:`stitchdatacontainer.strickend<createcloth.stitchinfo.load_stitchinfo.stitchdatacontainer.strickend>`.

.. todo::

   Redo stitchdatacontainer with the help of collections.abc.Container

Declaration via xmlfile
-----------------------

All information can be saved as xml-file. see 
createcloth.stitchinfo.stitches.xml



Reference of stitchinfo
-----------------------

.. automodule:: createcloth.stitchinfo
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: createcloth.stitchinfo.load_stitchinfo
   :members:
   :undoc-members:
   :show-inheritance:

..
        .. automodule:: createcloth.strickgraph.load_stitchinfo
           :members:
           :undoc-members:
