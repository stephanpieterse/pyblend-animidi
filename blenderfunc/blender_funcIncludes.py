# we need this to scale actions and keyframing right
def get_relative_action_scale(obj_s, obj_e, note_s, note_e):
    action_frames = obj_e - obj_s # 10 - 5 = 5
    note_frames = note_e - note_s # 1050 - 1025 = 25
    relative_scale = note_frames / float(action_frames) # 25 / 5.0 = 5

    return relative_scale


# this is needed so we don't super overextend the end frames needed position
def get_frame_shift(relative_scale, obj_s, obj_e):
    action_len = obj_e - obj_s # 10 - 5 = 5
    new_len = action_len * relative_scale # 5 * 5 = 25
    new_end = obj_s + new_len # 5 + 25 = 30

    return new_end


def buildContinueAction(curAction, newobj, noteStart, noteEnd):
    for i in curAction.fcurves:
        rna_index_exists = False
        for j in newobj.animation_data.action.fcurves:
            if (j.data_path == i.data_path) and (j.array_index == i.array_index) and (j.group.name == i.group.name):
                rna_index_exists = True

        if rna_index_exists is False:
            newfc = newobj.animation_data.action.fcurves.new(i.data_path,i.array_index,i.group.name)
        else:
            for j in newobj.animation_data.action.fcurves:
                if (j.data_path == i.data_path) and (j.array_index == i.array_index) and (j.group.name == i.group.name):
                    # newfc = newobj.animation_data.action.fcurves
                    newfc = j

        # we need to figure out where the action officially starts to scale everything right
        left_most_point = 100000.0
        right_most_point = 0.0
        for y in i.keyframe_points:
            if y.co.x <= left_most_point:
                left_most_point = y.co.x
            if y.co.x >= right_most_point:
                right_most_point = y.co.x

        actionRelScale = get_relative_action_scale(left_most_point,right_most_point,noteStart,noteEnd)

        fckp = len(newfc.keyframe_points) - 1
        for x in i.keyframe_points:
            if x.co.x == left_most_point:
                curX = bpy.context.scene.frame_current
                new_co = [curX + x.co.x, x.co.y]
                newfc.keyframe_points.add(1)
                newfc.keyframe_points[fckp].co = new_co
                newfc.keyframe_points[fckp].handle_left = [curX + x.handle_left.x, x.handle_left.y]
                newfc.keyframe_points[fckp].handle_left_type = x.handle_left_type
                newfc.keyframe_points[fckp].handle_right = [curX + x.handle_right.x, x.handle_right.y]
                newfc.keyframe_points[fckp].handle_right_type = x.handle_right_type
                newfc.keyframe_points[fckp].interpolation = x.interpolation
            else:
                curX = bpy.context.scene.frame_current
                new_co = [curX + get_frame_shift(actionRelScale,left_most_point,x.co.x),x.co.y]
                newfc.keyframe_points.add(1)
                newfc.keyframe_points[fckp].co = new_co
                newfc.keyframe_points[fckp].handle_left = [curX + get_frame_shift(actionRelScale,left_most_point,x.handle_left.x), x.handle_left.y]
                newfc.keyframe_points[fckp].handle_left_type = x.handle_left_type
                newfc.keyframe_points[fckp].handle_right = [curX + get_frame_shift(actionRelScale,left_most_point,x.handle_right.x), x.handle_right.y]

                newfc.keyframe_points[fckp].handle_right_type = x.handle_right_type
                newfc.keyframe_points[fckp].interpolation = x.interpolation
            fckp += 1


# our func to create objects that need to pop into the scene
def duplicateObject(scene, name, copy_obj):
    # Create new mesh
    mesh = bpy.data.meshes.new(name)
    # Create new object associated with the mesh
    ob_new = bpy.data.objects.new(name, mesh)
    copy_obj = bpy.data.objects[copy_obj]
    # Copy data block from the old object into the new object
    ob_new.data = copy_obj.data.copy()
    ob_new.scale = copy_obj.scale
    ob_new.location = copy_obj.location
    ob_new.rotation_euler = copy_obj.rotation_euler
    # uncomment this line if scene becomes bloaty and slow i guess
    # ob_new.hide = True
    ob_new.hide_render = False
    # Link new object to the given scene and select it
    scene.objects.link(ob_new)
    ob_new.select = True

    return ob_new.name


# this is just a wrapper so we don't have to specify nla values for fcurves
def populateActionFromListFCurve(action_list,action_object, calc_frame, start_frame, end_frame):
    return populateActionFromList(action_list,action_object, calc_frame, start_frame, end_frame, 'HOLD', 'REPLACE', False, 'FCURVE')


# mode can be either 'NLA' or 'FCURVE'
def populateActionFromList(action_list,action_object, calc_frame, start_frame, end_frame, nla_extrap, nla_blend, nla_autoblend, mode = 'NLA'):
    # take the start and end frames for each note, and space the actions specified into that space.
    # the total length should include: attack, note, (vibrato)
    # the prenote is not relative, and ENDS at the start of the attack frame action
    # the attack starts on the start_frame, and is not relative
    # the note immediately follows, and is relative (scaled)
    # if there is a vibrato, we should get the vibrato delay, then if the note holds long enough,
    #   shorten it and squeeze the vibrato into the rest of the space
    # the release follows immediately at the end frame, not relative.
    # i'm not really sure what to do with wait. release should end at the right spot?
    # IMPORTANT : even though some actions are not relative to the note duration,
    #   they ARE relative to the soundOptions in conf!
    # a note on blender: the nla strips support setting the start to a float number, but not inserting as.
    #   that's why we have a magic number one to just shift it for the insertion, and set it to where it should
    #   be right after.

    NLATrack = action_object.animation_data.nla_tracks.new()

    if 'prenote' in action_list.keys():
        curAction = bpy.data.actions[action_list['prenote']]
        action_length = curAction.frame_range.y - curAction.frame_range.x
        pre_start_frame = calc_frame - action_length
        if mode == 'NLA':
            CurStrip = NLATrack.strips.new("prenoteStrip", pre_start_frame+1, curAction)
            CurStrip.frame_start = pre_start_frame
            CurStrip.frame_end = pre_start_frame + action_length
            CurStrip.extrapolation = nla_extrap
            CurStrip.blend_type = nla_blend
            CurStrip.use_auto_blend = nla_autoblend
        elif mode == 'FCURVE':
            buildContinueActionV2(curAction, action_object, pre_start_frame, start_frame, end_frame, True)

    if 'attack' in action_list.keys():
        curAction = bpy.data.actions[action_list['attack']['action']]
        curActionTime = action_list['attack']['time']
        action_length = curAction.frame_range.y - curAction.frame_range.x
        if mode == 'NLA':
            CurStrip = NLATrack.strips.new("attackStrip", calc_frame+1, curAction)
            CurStrip.frame_start = calc_frame
            CurStrip.frame_end = calc_frame + action_length
            CurActionStart = CurStrip.frame_start
            CurActionEnd = CurStrip.frame_end
            actionRelScale = get_relative_action_scale(CurActionStart, CurActionEnd, 0, curActionTime)
            CurStrip.frame_end = get_frame_shift(actionRelScale,CurActionStart,CurActionEnd)
            AttackActionEnd = CurStrip.frame_end

            CurStrip.extrapolation = nla_extrap
            CurStrip.blend_type = nla_blend
            CurStrip.use_auto_blend = nla_autoblend
        elif mode == 'FCURVE':
            buildContinueActionV2(curAction, action_object, calc_frame, 0, curActionTime)
            calc_end = calc_frame + action_length
            actionRelScale = get_relative_action_scale(calc_frame, calc_end, 0, curActionTime)
            AttackActionEnd = get_frame_shift(actionRelScale, calc_frame, calc_end)
    else:
        AttackActionEnd = calc_frame

    if 'vibrato' in action_list.keys():
        noteAction = bpy.data.actions[action_list['note']]
        note_action_length = noteAction.frame_range.y - noteAction.frame_range.x
        vibratoAction = bpy.data.actions[action_list['vibrato']['action']]
        vibrato_action_length = vibratoAction.frame_range.y - vibratoAction.frame_range.x
        vibratoActionTime = action_list['vibrato']['time']
        NoteStrip = NLATrack.strips.new("noteStrip", AttackActionEnd+1, noteAction)

        actionRelScale = get_relative_action_scale(noteAction.frame_range.x, noteAction.frame_range.y, start_frame, end_frame)
        fullNoteEnd = get_frame_shift(actionRelScale, noteAction.frame_range.x, noteAction.frame_range.y)

        if note_action_length > vibratoActionTime:
            NoteStrip.frame_start = AttackActionEnd
            NoteStrip.frame_end = NoteStrip.frame_start + vibratoActionTime
            prevNoteStripEnd = NoteStrip.frame_end
            if mode == 'NLA':
                VibratoStrip = NLATrack.strips.new("vibratoStrip",NoteStrip.frame_end+1,vibratoAction)
                VibratoStrip.frame_start = NoteStrip.frame_end
                VibratoStrip.frame_end = fullNoteEnd
                VibratoStrip.extrapolation = nla_extrap
                VibratoStrip.blend_type = nla_blend
                VibratoStrip.use_auto_blend = nla_autoblend

            elif mode == 'FCURVE':
                buildContinueActionV2(vibratoAction, action_object, NoteStrip.frame_end, 0, vibratoActionTime)
            release_start = fullNoteEnd
            last_frame = fullNoteEnd
        else:
            if mode == 'NLA':
                NoteStrip.frame_start = AttackActionEnd
                NoteStrip.frame_end = AttackActionEnd + note_action_length
                NoteActionStart = NoteStrip.frame_start
                NoteActionEnd = NoteStrip.frame_end
                actionRelScale = get_relative_action_scale(NoteActionStart, NoteActionEnd, start_frame, end_frame)
                NoteStrip.frame_end = get_frame_shift(actionRelScale,NoteActionStart,NoteActionEnd)
                release_start = NoteStrip.frame_end
                last_frame = NoteStrip.frame_end
            elif mode == 'FCURVE':
                buildContinueActionV2(curAction, action_object, AttackActionEnd, start_frame, end_frame)
                action_end = AttackActionEnd + action_length
                actionRelScale = get_relative_action_scale(AttackActionEnd, action_end, start_frame, end_frame)
                release_start = get_frame_shift(actionRelScale, AttackActionEnd, action_end)

        NoteStrip.extrapolation = nla_extrap
        NoteStrip.blend_type = nla_blend
        NoteStrip.use_auto_blend = nla_autoblend

    else:
        curAction = bpy.data.actions[action_list['note']]
        action_length = curAction.frame_range.y - curAction.frame_range.x
        CurStrip = NLATrack.strips.new("noteStrip", AttackActionEnd+1, curAction)
        if mode == 'NLA':
            CurStrip.frame_start = AttackActionEnd
            CurStrip.frame_end = AttackActionEnd + action_length
            CurActionStart = CurStrip.frame_start
            CurActionEnd = CurStrip.frame_end
            actionRelScale = get_relative_action_scale(CurActionStart, CurActionEnd, start_frame, end_frame)
            CurStrip.frame_end = get_frame_shift(actionRelScale, CurActionStart, CurActionEnd)
            release_start = CurStrip.frame_end
            last_frame = CurStrip.frame_end
            CurStrip.extrapolation = nla_extrap
            CurStrip.blend_type = nla_blend
            CurStrip.use_auto_blend = nla_autoblend
        elif mode == 'FCURVE':
            buildContinueActionV2(curAction, action_object, AttackActionEnd, start_frame, end_frame)
            action_end = AttackActionEnd + action_length
            actionRelScale = get_relative_action_scale(AttackActionEnd, action_end, start_frame, end_frame)
            release_start = get_frame_shift(actionRelScale, AttackActionEnd, action_end)

    if 'release' in action_list.keys():
        curAction = bpy.data.actions[action_list['release']['action']]
        curActionTime = action_list['release']['time']
        action_length = curAction.frame_range.y - curAction.frame_range.x
        if mode == 'NLA':
            CurStrip = NLATrack.strips.new("releaseStrip", release_start+1, curAction)
            CurStrip.frame_start = release_start
            CurStrip.frame_end = release_start + action_length
            CurActionStart = CurStrip.frame_start
            CurActionEnd = CurStrip.frame_end
            actionRelScale = get_relative_action_scale(CurActionStart, CurActionEnd, 0, curActionTime)
            CurStrip.frame_end = get_frame_shift(actionRelScale,CurActionStart,CurActionEnd)
            last_frame = CurStrip.frame_end
            CurStrip.extrapolation = nla_extrap
            CurStrip.blend_type = nla_blend
            CurStrip.use_auto_blend = nla_autoblend
        elif mode == 'FCURVE':
            buildContinueActionV2(curAction, action_object, release_start, 0, curActionTime)
            actionRelScale = get_relative_action_scale(curAction.frame_range.x, curAction.frame_range.y, 0, curActionTime)
            last_frame = get_frame_shift(actionRelScale,curAction.frame_range.x,curAction.frame_range.y)

    # return the last frame so we can do the kill action
    return last_frame


def buildContinueActionV2(curAction, newobj, startFrame, noteStart, noteEnd, noRescale = False):
    for i in curAction.fcurves:
        rna_index_exists = False
        for j in newobj.animation_data.action.fcurves:
            if (j.data_path == i.data_path) and (j.array_index == i.array_index) and (j.group.name == i.group.name):
                rna_index_exists = True

        if rna_index_exists is False:
            newfc = newobj.animation_data.action.fcurves.new(i.data_path,i.array_index,i.group.name)
        else:
            for j in newobj.animation_data.action.fcurves:
                if (j.data_path == i.data_path) and (j.array_index == i.array_index) and (j.group.name == i.group.name):
                    newfc = j
                    break

        # we need to figure out where the action officially starts to scale everything right
        left_most_point = 100000.0
        right_most_point = 0.0
        for y in i.keyframe_points:
            if y.co.x <= left_most_point:
                left_most_point = y.co.x
            if y.co.x >= right_most_point:
                right_most_point = y.co.x

        if noRescale:
            actionRelScale = 1.0
        else:
            actionRelScale = get_relative_action_scale(left_most_point,right_most_point,noteStart,noteEnd)

        fckp = len(newfc.keyframe_points) - 1
        for x in i.keyframe_points:
            if x.co.x == left_most_point:
                curX = startFrame
                new_co = [curX + x.co.x, x.co.y]
                newfc.keyframe_points.add(1)
                newfc.keyframe_points[fckp].co = new_co
                newfc.keyframe_points[fckp].handle_left = [curX + x.handle_left.x, x.handle_left.y]
                newfc.keyframe_points[fckp].handle_left_type = x.handle_left_type
                newfc.keyframe_points[fckp].handle_right = [curX + x.handle_right.x, x.handle_right.y]
                newfc.keyframe_points[fckp].handle_right_type = x.handle_right_type
                newfc.keyframe_points[fckp].interpolation = x.interpolation
            else:
                curX = startFrame
                new_co = [curX + get_frame_shift(actionRelScale,left_most_point,x.co.x),x.co.y]
                newfc.keyframe_points.add(1)
                newfc.keyframe_points[fckp].co = new_co
                newfc.keyframe_points[fckp].handle_left = [curX + get_frame_shift(actionRelScale,left_most_point,x.handle_left.x), x.handle_left.y]
                newfc.keyframe_points[fckp].handle_left_type = x.handle_left_type
                newfc.keyframe_points[fckp].handle_right = [curX + get_frame_shift(actionRelScale,left_most_point,x.handle_right.x), x.handle_right.y]
                newfc.keyframe_points[fckp].handle_right_type = x.handle_right_type
                newfc.keyframe_points[fckp].interpolation = x.interpolation
            fckp += 1

# END DEFS
