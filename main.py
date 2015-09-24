import blenderfunc as bf
from config import *
from midiUtils import *
import pythonmidi

"""
 Copyright (C) 2015 Stephan Pieterse

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

class animidi:
    note_dataset = []
    midiResolution = 480
    BPM = 120
    FPS = 25
    configFile = ""

    def __init__(self,configFile = "config.yml"):
        self.configFile = configFile

    def build_dataset_from_midi(self):
        confFile = configParser(self.configFile)
        midifilename = confFile.getConfig('midifile')
        confOptions = confFile.getConfig('options')
        noteOffDefault = confOptions['noteOffDefaultTime']

        midifile = midifilename['name']
        pattern = pythonmidi.read_midifile(midifile)
        midiResolution = pattern.resolution
        self.midiResolution = midiResolution

        fps = confOptions['blendFramerate']
        self.FPS = fps
        frame_range = [ confOptions['frameStart'],confOptions['frameEnd'] ]

        tx = 0
        found_tempo = False
        while tx < len(pattern):
            track = pattern[tx]
            i = len(track)
            x = 0
            while x < i:
                tname = track[x].name
                if tname == "Set Tempo":
                    BPM = track[x].bpm
                    self.BPM = BPM
                    found_tempo = True
                x += 1
            tx += 1
            if found_tempo is True:
                break

        midiUtil = midiUtility(self.midiResolution,self.BPM,self.FPS)

        # if pattern.tick_relative == False:
        pattern.make_ticks_rel()
        print "making ticks relative..."
        globalNote = 0
        tx = 0
        while tx < len(pattern):
            print "reading track {} of {}".format(tx, len(pattern) - 1)

            track = pattern[tx]
            i = len(track)
            globalTick = 0

            x = 0
            while x < i:
                tname = track[x].name
                ntick = track[x].tick
                globalTick = globalTick + ntick
                whichFrame = midiUtil.tickToFrame(globalTick)

                if not whichFrame in range(frame_range[0],frame_range[1]):
                    x = x + 1
                    continue

                if tname == "Note On":
                    cur_chan = track[x].channel
                    cur_pitch = track[x].data[0]
                    self.note_dataset.append(globalNote)

                    globalTick = globalTick + ntick
                    whichFrame = midiUtil.tickToFrame(globalTick)

                    if track[x].data[1] == 0:
                        prevnvel = nvel
                        nvel = prevnvel
                    else:
                        nvel = track[x].data[1]

                    this_end_frame = -1
                    relative_tick = 0
                    j = x
                    while j < i:
                        jname = track[j].name
                        relative_tick += track[j].tick
                        if jname == "Note Off" and track[j].data[0] == cur_pitch:
                            this_end_frame = midiUtil.tickToFrame(globalTick + relative_tick)
                            break
                        j += 1

                    if this_end_frame == -1:
                        this_end_frame = midiUtil.tickToFrame(globalTick)
                        this_end_frame += midiUtil.millisecondsToFrames(noteOffDefault)
                    self.note_dataset[globalNote] = {'channel': cur_chan, 'pitch': cur_pitch, 'velocity': nvel, 'start_frame': whichFrame, 'end_frame': this_end_frame}
                    globalNote += 1
                x += 1

            print "built track {}".format(tx)
            tx += 1

    def build_dataset_from_csv(self):
        print("building dataset... please be patient...")
        confFile = configParser(self.configFile)
        midifilename = confFile.getConfig('midifile')
        midifile = midifilename['name']
        confOptions = confFile.getConfig('options')
        noteOffDefault = confOptions['noteOffDefaultTime']

        with open(midifile) as f:
            lines = f.readlines()
            for line in lines:
                linesplit = line.split(',')
                ttype = linesplit[2].strip(" ")
                if(int(linesplit[0])) == 0 and ttype == "Header":
                    midiResolution = int(linesplit[5])
                    self.midiResolution = midiResolution
                if(int(linesplit[0])) == 1 and ttype == "Tempo":
                    BPM = 60000000.0 / int(linesplit[3])
                    self.BPM = BPM
            f.close()

        fps = confOptions['blendFramerate']
        self.FPS = fps
        frame_range = [ confOptions['frameStart'],confOptions['frameEnd'] ]

        midiUtil = midiUtility(self.midiResolution,self.BPM,self.FPS)

        globalNote = 0
        with open(midifile) as f:
            lines = f.readlines()
            for cmddata in lines:
                line = cmddata.split(',')
                tname = line[2]

                ntick = int(line[1])
                whichFrame = midiUtil.tickToFrame(ntick)

                if whichFrame < frame_range[0] or whichFrame > frame_range[1]:
                     continue

                tname = tname.lower()
                tname = tname.strip(" ")
                if tname == "note_on_c":
                    # the channel
                    cur_chan = int(line[0])
                    # the pitch
                    cur_pitch = int(line[4])
                    # the velocity
                    nvel = int(line[5])
                    self.note_dataset.append(globalNote)

                    this_end_frame = -1
                    for cmddata2 in lines:
                        line2 = cmddata2.split(',')
                        jname = line2[2]
                        jname = jname.lower()
                        jname = jname.strip(" ")

                        if jname == "note_off_c":
                            this_channel = int(line2[0])
                            this_pitch = int(line2[4])
                            this_tick = int(line2[1])
                            if this_channel == cur_chan and this_pitch == cur_pitch and this_tick >= ntick:
                                this_end_frame = midiUtil.tickToFrame(this_tick)
                                break

                    if this_end_frame == -1:
                        this_end_frame = midiUtil.tickToFrame(this_tick)
                        this_end_frame += midiUtil.millisecondsToFrames(noteOffDefault)

                    insert_data = {'channel': cur_chan, 'pitch': cur_pitch, 'velocity': nvel, 'start_frame': whichFrame, 'end_frame': this_end_frame}
                    self.note_dataset[globalNote] = insert_data
                    globalNote += 1
        f.close()
        print("done building dataset...")

    # utility function
    def cycle_number(self,num,max):
        num += 1
        if num <= max:
            return num
        else:
            return 0

    def main(self):
        print("starting script...")
        confFile = configParser(self.configFile)
        inputOptions = confFile.getConfig("midifile")
        inputMode = inputOptions["mode"]
        if inputMode == "csv":
            self.build_dataset_from_csv()
        elif inputMode == "midi":
            self.build_dataset_from_midi()

        print("mapping data to objects...")

        confOptions = confFile.getConfig('options')
        outConfig = confFile.getConfig("scriptOutput")
        outputScriptName = outConfig["name"]

        print "clearing the script output file..."
        with open(outputScriptName, 'w') as f:
            baseScript = "#autogenerated. edit at own risk. animidi \nimport bpy \n"
            f.write(baseScript)

            # include all our reusable functions in the blender script.
            with open("blenderfunc/blender_funcIncludes.py", 'r') as fi:
                funcIncludes = fi.read()
                fi.close()

            f.write(funcIncludes)
            f.close

        # blender objects - will be modified later on
        bObjs = confFile.getConfig('blenderobjects')
        # all objects - a copy that stays the same.
        aObjs = confFile.getConfig('blenderobjects')

        try:
            should_cycle = confOptions['parseCycleSequences']
        except KeyError:
            should_cycle = False

        if should_cycle:
            cycleList = []
            cycleChannels = []
            cycleConfs = confFile.getConfig("cycle_sequences")
            cycx = 0
            for cset in cycleConfs:
                cycleList.append(cycx)
                cycleChannels.append(cycx)
                cycleList[cycx] = {}
                cycleChannels.append(cycx)
                cycleChannels[cycx] = cycleConfs[cset]["channel"]
                inum = 0
                for i in cycleConfs[cset]["cycle_objects"].split(","):
                    i = i.strip(" ")
                    cycleList[cycx][inum] = i
                    if i in bObjs:
                        del bObjs[i]
                    inum += 1
                cycx += 1

            # this is still part of shoudCycle!
            # we need this to keep track of our channel
            cSetPos = 0
            for cSet in cycleList:
                cObjs = []
                cyclePos = 0
                cycleMax = len(cSet) - 1
                cycleChannel = cycleChannels[cSetPos]
                # create a cycle list
                ic = 0
                for co in cSet:
                    cObjs.append(ic)
                    coName = cSet[co]
                    cObjs[ic] = bf.BlenderObj(coName, confFile, self.midiResolution, self.BPM)
                    cObjs[ic].set_framerate(self.FPS)
                    ic += 1

                # for each note, check channel, do the object, change the cycle pos.
                for note_event in self.note_dataset:
                    if note_event['channel'] == cycleChannel:
                        cObjs[cyclePos].insert_note(cycleChannel,note_event['pitch'],note_event['velocity'],note_event['start_frame'],note_event['end_frame'])
                        cyclePos = self.cycle_number(cyclePos,cycleMax)

                # write all the cycled objects scripts to file, finally
                for cObj in cObjs:
                    cObj.write_blender_script()

                # move to the next objects means moving the channel
                cSetPos += 1

        # parse the existing / remaining blenderObjects, and send them to the animator.
        for bObj in bObjs:
            boName = bObj  # bObjs[bObj]['name']
            boChannel = bObjs[bObj]['channel']
            bo = bf.BlenderObj(boName, confFile,self.midiResolution,self.BPM)
            bo.set_framerate(self.FPS)
            for note_event in self.note_dataset:
                if note_event['channel'] == boChannel:
                    bo.insert_note(boChannel,note_event['pitch'],note_event['velocity'],note_event['start_frame'],note_event['end_frame'])

            bo.write_blender_script()

        # do the fcurve handle refreshing. no longer used really. the clean messes up our keyframes.
        with open("blenderfunc/blender_endScriptRefresh.py",'r') as f:
            last_action = f.read()
            f.close()

        # set the scene frame back to 1.
        with open(outputScriptName, 'a') as f:
            f.write("bpy.context.scene.frame_set(1)\n")
            f.write(last_action)
            f.close()

        print "you can now import the script {} into blender and run it.".format(outputScriptName)
