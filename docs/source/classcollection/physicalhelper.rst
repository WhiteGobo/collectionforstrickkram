Physicalhelper
==============

Physical properties
-------------------

Everything, that has something to do with physical properties is touched by 
this module. This should range from properties, used in simulations, till optimal length of an row of the knitting piece.

Threadinfo
----------

The used thread has a major role, in determining, what the physical
properties are. The data of the thread is implemented by the class
:py:class:`createecloth.physicalhelper.edgelength_helper.threadinfo`.

.. todo::

   threadinfo has many similarities to stitchtypes and strickdata. So maybe
   it should be trnsferred to the corresponding module

optimal rowlength
-----------------

Rowlength is currently not directed immplemented. Instead there is an optimal 
edgelength implemented via 
:py:func:`singleedge_length<createcloth.physical_helper.edgelength_helper.singleedge_length>`.

how this used can be seen in sourcecode to
:py:data:`clothfactory_parts.physics.strickgraph_physics_factoryleafs.test_if_strickgraph_isrelaxed`.

.. code::

   from createcloth.physical_helper import standardthreadinfo as mythreadinfo
   lengthforextrastitch = singleedge_length( "knit", "knit", "next", \
                                                        mythreadinfo )


How it this module is used in simulations
-----------------------------------------

See :py:mod:`createcloth.meshhandler` for this.

.. todo::

   fill this with content:)


Reference
---------

.. automodule:: createcloth.physicalhelper
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: createcloth.physicalhelper.edgelength_helper
   :members:
   :undoc-members:
   :show-inheritance:
