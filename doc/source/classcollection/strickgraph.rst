Strickgraph
===========

.. py:class:: createcloth.strickgraph.strickgraph

   **Manualmethods:**

   .. automethod:: to_manual
   .. automethod:: from_manual

   **Abstractgenerators:**

   .. automethod:: from_gridgraph

   **Physicmethods:**

   .. automethod:: set_calmlength
   .. automethod:: set_positions

   **Organizemethods:**

   .. automethod:: find_following_row
   .. automethod:: give_real_graph
   .. automethod:: get_borders
   .. automethod:: get_rows
   .. automethod:: get_startside
   .. automethod:: give_next_node_to
   .. automethod:: get_connected_nodes
   .. automethod:: get_sidemargins
   .. automethod:: get_sidemargins_indices

   **Stitchinfo-thingies**

   .. automethod:: get_alternative_stitchtypes
   .. automethod:: copy_with_alternative_stitchtype

   **Strickgraph as Graph**

   .. automethod:: get_startstitch
   .. automethod:: get_endstitch

   .. automethod:: get_nodes
   .. automethod:: get_nodes_near_nodes
   .. automethod:: get_nodeattributes
   .. automethod:: get_edges_with_labels
   .. automethod:: get_nodeattributelabel
   
   **available attributes**

   allnodes: stitchtype, side
   somenodes: startingpoint, alternativestitchtype

   .. automethod:: get_nodeattr_stitchtype
   .. automethod:: get_nodeattr_side
   .. automethod:: get_nodeattr_startingpoint
   .. automethod:: get_nodeattr_alternativestitchtype
