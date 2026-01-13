from pysynth import Synthesizer, Note, Wave

synth = Synthesizer(100, Wave.Square, True) # default settings, 100ms square wave

notes = [
    Note('C4'),
    Note('E4'),
    Note('G4'),
    Note('E4'),
    Note('C4')
]

synth.play_note(notes)
