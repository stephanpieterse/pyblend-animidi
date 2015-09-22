killAction = bpy.data.actions.new("this_killer")
newfc = killAction.fcurves.new('hide_render',0)
newfc.keyframe_points.add(2)
newfc.keyframe_points[0].co = [0,0]
newfc.keyframe_points[1].co = [1,1]
newfc.keyframe_points[0].interpolation = 'CONSTANT'
newfc.keyframe_points[1].interpolation = 'CONSTANT'

NLATrack = %ACTION_OBJ%.animation_data.nla_tracks.new()
CurStrip = NLATrack.strips.new("killStrip",killFrame,killAction)
CurStrip.frame_start = killFrame
CurStrip.frame_end = killFrame + 1.0
