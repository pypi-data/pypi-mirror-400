from math import pi

import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
from librosa import note_to_hz

from .note import Note
from .wave import Wave


class Synthesizer:
    def __init__(self, default_nlen: int, default_wave: Wave, show_vis: bool) -> None:
        self.samplerate = 44100
        self.default_nlen = default_nlen
        self.default_wave = default_wave
        self.show_vis = show_vis
        if show_vis:
            plt.ion()
            self.fig, self.ax = plt.subplots(figsize=(10, 4))

    def play_frq(self, frq: float, sec: float, wave: Wave) -> None:
        nsamples = self.samplerate * sec
        phase_values = np.arange(nsamples) * (2 * pi * frq / self.samplerate)

        if wave == Wave.Sine:
            audio = np.sin(phase_values)
        elif wave == Wave.Square:
            audio = np.sign(np.sin(phase_values))
        elif wave == Wave.Saw:
            audio = 2 * (phase_values / (2 * pi) % 1) - 1
        elif wave == Wave.Triangle:
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

        audio = audio.astype(np.float32)

        sd.play(audio, self.samplerate)
        sd.wait()

    def get_hz(self, name: str) -> float:
        return float(note_to_hz(name))
    def get_len(self, ms: float|None) -> float:
        return ms / 1000 if ms is not None else self.default_nlen / 1000
    def get_wave(self, wave: Wave|None) -> Wave:
        return wave if wave is not None else self.default_wave

    def play_note(self, note: Note|list[Note]) -> None:
        if isinstance(note, Note):
            self.play_frq(
                self.get_hz(note.name),
                self.get_len(note.ms),
                self.get_wave(note.wave)
            )
        elif isinstance(note, list):
            for nt in note:
                self.play_frq(
                    self.get_hz(nt.name),
                    self.get_len(nt.ms),
                    self.get_wave(nt.wave)
                )

    def play_notes_ww(self, note: Note|list[Note], wave: Wave) -> None:
        if isinstance(note, Note):
            self.play_note(Note(note.name, note.ms, wave))
        elif isinstance(note, list):
            self.play_note(list(Note(nt.name, nt.ms, wave) for nt in note))


    def play_sine(self, note: Note|list[Note]) -> None:
        self.play_notes_ww(note, Wave.Sine)
    def play_square(self, note: Note|list[Note]) -> None:
        self.play_notes_ww(note, Wave.Square)
    def play_saw(self, note: Note|list[Note]) -> None:
        self.play_notes_ww(note, Wave.Saw)
    def play_triangle(self, note: Note|list[Note]) -> None:
        self.play_notes_ww(note, Wave.Triangle)
