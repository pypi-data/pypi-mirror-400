from pyaudiosynth import Synthesizer, Note, Wave

def main():
    synth = Synthesizer(250, Wave.Square, True) # default settings, 100ms square wave

    synth.play_note(Note('C4', ms=500, wave=Wave.Sine))

    notes = [
        Note('C4'),
        Note('E4'),
        Note('G4'),
        Note('E4'),
        Note('C4')
    ]

    synth.play_sine(notes)
    synth.play_square(notes)
    synth.play_saw(notes)
    synth.play_triangle(notes)
