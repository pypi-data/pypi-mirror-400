from math import pi

import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
from librosa import note_to_hz

from .note import Note
from .wave import Wave

class Synthesizer:
    """
    Main class for synthesizing notes

    :param default_nlen: The default note length in milliseconds (default 500)
    :type default_nlen: int
    :param default_wave: The default waveform to use (default Sine)
    :type default_wave: Wave
    :param show_vis: If we should show the waveform visualisation (default False)
    :type show_vis: bool
    """

    def __init__(self, default_nlen: int = 500, default_wave: Wave = Wave.Sine, show_vis: bool = False) -> None:
        self.samplerate = 44100
        self.default_nlen = default_nlen
        self.default_wave = default_wave
        self.show_vis = show_vis
        if show_vis:
            plt.ion()
            self.fig, self.ax = plt.subplots(figsize=(10, 4))

    def play_frq(self, frq: float, ms: float, wave: Wave) -> None:
        """
        Plays a certain frequency

        :param frq: The frequency to play
        :type frq: float
        :param ms: Milisecconds to play the note for
        :type ms: float
        :param wave: The waveform to play
        :type wave: Wave
        """

        nsamples = self.samplerate * (ms / 1000)
        phase_values = np.arange(nsamples) * (2 * pi * frq / self.samplerate)

        match wave:
            case Wave.Sine:
                audio = np.sin(phase_values)
            case Wave.Square:
                audio = np.sign(np.sin(phase_values))
            case Wave.Saw:
                audio = 2 * (phase_values / (2 * pi) % 1) - 1
            case Wave.Triangle:
                audio = 2 * np.abs(2 * (phase_values / (2 * pi) % 1) - 1) - 1

        if self.show_vis:
            self.ax.clear()
            samples_to_show = int(0.01 * self.samplerate)
            time = np.arange(samples_to_show) / self.samplerate
            self.ax.plot(time, audio[:samples_to_show])
            self.ax.set_xlabel('Time (s)')
            self.ax.set_ylabel('Amplitude')
            self.ax.set_title(f'{wave.name.capitalize()} wave - {frq:.1f} Hz')
            self.ax.grid(True)
            self.ax.set_ylim(-1.5, 1.5)
            plt.draw()
            plt.pause(0.001)

        sd.play(audio.astype(np.float32), self.samplerate)
        sd.wait()

    def play_note(self, note: Note|list[Note]) -> None:
        """
        Plays note(s)

        :param note: The note, or list of notes to play
        :type note: Note|list[Note]
        """

        self.play_frq(
            float(note_to_hz(note.name)),
            note.ms if note.ms is not None else self.default_nlen,
            note.wave if note.wave is not None else self.default_wave
        ) if isinstance(note, Note) else tuple(self.play_note(nt) for nt in note) # tuple forces execution

    def play_notes_ww(self, note: Note|list[Note], wave: Wave) -> None:
        """
        Plays note(s), ignoring the notes waveform instead using the provided waveform

        :param note: The note, or list of notes to play
        :type note: Note|list[Note]
        :param wave: The waveform which we should play
        :type wave: Wave
        """

        self.play_note(
            list(Note(nt.name, nt.ms, wave) for nt in note)
            if isinstance(note, list)
            else Note(note.name, note.ms, wave)
        )

    def play_sine(self, note: Note|list[Note]) -> None:
        """
        Plays note(s), ignoring the notes waveform instead using a Sine wave

        :param note: The note, or list of notes to play
        :type note: Note|list[Note]
        """

        self.play_notes_ww(note, Wave.Sine)

    def play_square(self, note: Note|list[Note]) -> None:
        """
        Plays note(s), ignoring the notes waveform instead using a Square wave

        :param note: The note, or list of notes to play
        :type note: Note|list[Note]
        """

        self.play_notes_ww(note, Wave.Square)

    def play_saw(self, note: Note|list[Note]) -> None:
        """
        Plays note(s), ignoring the notes waveform instead using a Sawtooth wave

        :param note: The note, or list of notes to play
        :type note: Note|list[Note]
        """

        self.play_notes_ww(note, Wave.Saw)

    def play_triangle(self, note: Note|list[Note]) -> None:
        """
        Plays note(s), ignoring the notes waveform instead using a Triangle wave

        :param note: The note, or list of notes to play
        :type note: Note|list[Note]
        """

        self.play_notes_ww(note, Wave.Triangle)
