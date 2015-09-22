C = bpy.context
old_area_type = C.area.type
C.area.type = 'GRAPH_EDITOR'
# bpy.ops.graph.clean(threshold = 0.00001)
C.area.type = old_area_type