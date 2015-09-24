# START ACTION
bpy.context.scene.frame_set(%CALCULATED_FRAME%)
calc_frame = %CALCULATED_FRAME%

noteStart = %NOTE_START_FRAME%
noteEnd = %NOTE_END_FRAME%

curAction = "%PITCH_ACTION%"
curPreNoteAction = "%PRENOTE_ACTION%" # curPreNoteAction = bpy.data.actions["%PRENOTE_ACTION%"]
curAttackAction = "%ATTACK_ACTION%" # curAttackAction = bpy.data.actions["%ATTACK_ACTION%"]
curAttackTime = %ATTACK_TIME%
curReleaseAction = "%RELEASE_ACTION%" # curReleaseAction = bpy.data.actions["%RELEASE_ACTION%"]
curReleaseTime = %RELEASE_TIME%
curVibratoAction = "%VIBRATO_ACTION%" # curVibratoAction = bpy.data.actions["%VIBRATO_ACTION%"]
curVibratoTime = 0
# restAction = bpy.data.actions["%REST_ACTION%"]
%DUPLICATE_ME_SECTION%

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

populateActionFromListFCurve(action_list, actionObj, calc_frame, noteStart, noteEnd)
# curAction = bpy.data.actions[curAction]
# buildContinueAction(curAction, newobj, noteStart, noteEnd)
# buildContinueAction(restAction, newobj, noteEnd+2, noteEnd+5)
actionObj.select = True
# todo we need a kill action, that calls buildcontinueaction
# END ACTION
