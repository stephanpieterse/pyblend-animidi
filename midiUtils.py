__author__ = 'stephan'

class midiUtility:
    midiResolution = 480
    FPS = 25
    BPM = 120

    def __init__(self, midiResolution, BPM, FPS):
        self.midiResolution = midiResolution
        self.FPS = FPS
        self.BPM = BPM

    def tickToFrame(self,tick):
        tpqn = self.midiResolution
        fpm = self.FPS * 60
        tpm = tpqn * self.BPM
        tpf = tpm / float(fpm)
        if tick > 0:
            frame = tick / tpf
        else:
            frame = -(tick/tpf)
        return frame

    def millisecondsToFrames(self, milliseconds):
        fps = self.FPS # 25
        inSeconds = milliseconds / 1000.0 # 250 / 1000.0 = 0.25
        frames = fps * inSeconds # 25 * .025 = 6.25

        return frames
