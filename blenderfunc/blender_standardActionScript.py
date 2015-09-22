# START INSERT
curAction = "%PITCH_ACTION%"
curPreNoteAction = "%PRENOTE_ACTION%" # curPreNoteAction = bpy.data.actions["%PRENOTE_ACTION%"]
curAttackAction = "%ATTACK_ACTION%" # curAttackAction = bpy.data.actions["%ATTACK_ACTION%"]
curAttackTime = %ATTACK_TIME%
curReleaseAction = "%RELEASE_ACTION%" # curReleaseAction = bpy.data.actions["%RELEASE_ACTION%"]
curReleaseTime = %RELEASE_TIME%
curVibratoAction = "%VIBRATO_ACTION%" # curVibratoAction = bpy.data.actions["%VIBRATO_ACTION%"]
curVibratoTime = %VIBRATO_TIME%
# restAction = bpy.data.actions["%REST_ACTION%"]

action_list = {}
if curAction != "":
    action_list['note'] = curAction
if curPreNoteAction != "":
    action_list['prenote'] = curPreNoteAction
if curAttackAction != "":
    action_list['attack'] = { 'action': curAttackAction, 'time': curAttackTime}
if curVibratoAction != "":
    action_list['vibrato'] = { 'action': curVibratoAction, 'time': curVibratoTime}
if curReleaseAction != "":
    action_list['release'] = { 'action': curReleaseAction, 'time': curReleaseTime}

noteStart = %NOTE_START_FRAME%
noteEnd = %NOTE_END_FRAME%

actionStartFrame = %CALCULATED_FRAME%
bpy.context.scene.frame_set(%CALCULATED_FRAME%)
actionObj = %ACTION_OBJ%
%DUPLICATE_ME_SECTION%

%NLA_BLENDS%

last_frame = populateActionFromList(action_list, actionObj, actionStartFrame, noteStart, noteEnd, nla_extrap, nla_blend, nla_autoblend)
killFrame = last_frame
%DUPLI_KILL%
# END INSERT
