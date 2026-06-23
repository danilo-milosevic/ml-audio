from enum import Enum
import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
from scipy.io import wavfile

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from load.load import load_wav_as_float
from transform.quantize import quantize_bits
from transform.sample_rate import change_sample_rate
from util.util import to_int16, spectrum_db

import sounddevice as sd


class State(Enum):
    NO_FILE = 1,
    LOADED = 2,
    MODIFIED = 3,
    PLAYING = 4,
    SAVING = 5

class AudioDigitApp(tk.Tk):

    BIT_OPTIONS = [2, 4, 6, 8, 10, 12, 14, 16]
    SR_OPTIONS = [6000, 8000, 16000, 22050, 32000, 44100]

    def __init__(self):
        super().__init__()
        self.title("Demonstracija digitalizacije audio signala")
        self.geometry("1000x700")

        self.signal = None
        self.fs_orig = None
        self.modified = None
        self.state = None
        self.file_label = tk.StringVar(value="")

        self._build_ui()

    def _configure_ui_state(self):
        self.btn_play_orig.config(state = "normal" if self.state in [State.LOADED, State.MODIFIED] else "disabled")
        self.btn_play_mod.config(state = "normal" if self.state in [State.MODIFIED] else "disabled")
        self.stop_btn.config(state = "normal" if self.state in [State.PLAYING] else "disabled")
        self.btn_save.config(state = "normal" if self.state in [State.MODIFIED] else "disabled")
        self.modify_button.config(state = "normal" if self.state in [State.LOADED, State.MODIFIED] else "disabled")
        self.load_btn.config(state = "normal" if self.state in [State.NO_FILE, State.LOADED, State.MODIFIED] else "disabled")

    def _update_state(self, new_state):
        self.state = new_state
        self._configure_ui_state()

    def _build_ui(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        self.load_btn = ttk.Button(top, text="Učitaj .wav", command=self.on_load_file)
        self.load_btn.pack(side="left", padx=(0, 10))
        ttk.Label(top, textvariable=self.file_label).pack(side="left")

        controls = ttk.Frame(self, padding=(10, 0, 10, 10))
        controls.pack(fill="x")

        ttk.Label(controls, text="Broj bita:").pack(side="left")
        self.bits_var = tk.StringVar(value=str(self.BIT_OPTIONS[-1]))
        ttk.Combobox(controls, textvariable=self.bits_var, state="readonly", width=6,
                     values=[str(b) for b in self.BIT_OPTIONS]).pack(side="left", padx=(5, 20))

        ttk.Label(controls, text="Frekvencija odmeravanja:").pack(side="left")
        self.sr_var = tk.StringVar(value=str(self.SR_OPTIONS[-1]))
        ttk.Combobox(controls, textvariable=self.sr_var, state="readonly", width=8,
                     values=[str(s) for s in self.SR_OPTIONS]).pack(side="left", padx=(5, 20))

        self.modify_button = ttk.Button(controls, text="Modifikuj", command=self.on_apply)
        self.modify_button.pack(side="left")

        buttons = ttk.Frame(self, padding=(10, 0, 10, 10))
        buttons.pack(fill="x")

        self.btn_play_orig = ttk.Button(buttons, text="Pusti original",
                   command=lambda: self.play(self.signal, self.fs_orig))
        self.btn_play_orig.pack(side="left", padx=(0, 8))

        self.btn_play_mod = ttk.Button(buttons, text="Pusti modifikovan",
                                        command=self._play_modified)
        self.btn_play_mod.pack(side="left", padx=(0, 8))

        self.stop_btn = ttk.Button(buttons, text="Zaustavi", command=self.stop)
        self.stop_btn.pack(side="left", padx=(0, 8))

        self.btn_save = ttk.Button(buttons, text="Sačuvaj modifikovan", command=self.on_save)
        self.btn_save.pack(side="left")

        self.fig = Figure(figsize=(9, 5.5), dpi=100)
        self.ax_orig = self.fig.add_subplot(211)
        self.ax_mod = self.fig.add_subplot(212)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._update_state(State.NO_FILE)

    def on_load_file(self):
        path = filedialog.askopenfilename(title="Izaberi .wav fajl", filetypes=[("WAV fajlovi", "*.wav")])
        if not path:
            return
        try:
            sig, fs, bits = load_wav_as_float(path)
        except Exception as e:
            messagebox.showerror("Greška", f"Greška pri učitavanju:\n{e}")
            return

        self.signal, self.fs_orig = sig, fs
        self.modified = None
        self.file_label.set(f"{os.path.basename(path)}   |   fs = {fs} Hz   |   {bits} bit(a)")
        self._update_state(State.LOADED)

        self._plot(self.ax_orig, sig, fs, "Spektar originalnog signala", "#2255aa")
        self.ax_mod.clear()
        self.canvas.draw()

    def on_apply(self):
        if self.signal is None:
            messagebox.showwarning("Greška", "Prvo učitajte .wav fajl.")
            return

        n_bits = int(self.bits_var.get())
        fs_new = int(self.sr_var.get())

        resampled = change_sample_rate(self.signal, self.fs_orig, fs_new)
        quantized = quantize_bits(resampled, n_bits)
        self.modified = (quantized, fs_new, n_bits)

        self._plot(self.ax_mod, quantized, fs_new,
                   f"Spektar modifikovanog — fs={fs_new} Hz, {n_bits} bit(a)", "#cc4400")
        self._update_state(State.MODIFIED)


    def _plot(self, ax, sig, fs, title, color):
        f, mag = spectrum_db(sig, fs)
        ax.clear()
        ax.plot(f, mag, color=color, linewidth=0.7)
        ax.set_title(title)
        ax.set_xlabel("frekvencija [Hz]")
        ax.set_ylabel("magnituda [dB]")
        ax.set_xlim(0, fs / 2)
        ax.set_ylim(-100, 5)
        self.fig.tight_layout()
        self.canvas.draw()

    def on_save(self):
        if self.modified is None:
            return
        sig, fs, n_bits = self.modified
        self._update_state(State.SAVING)
        path = filedialog.asksaveasfilename(
            title="Sačuvaj modifikovan signal",
            defaultextension=".wav",
            initialfile=f"signal_{n_bits}bit_{fs}Hz.wav",
            filetypes=[("WAV fajl", "*.wav")],
        )
        self._update_state(State.MODIFIED)
        if not path:
            return
        wavfile.write(path, fs, to_int16(sig))
        messagebox.showinfo("Sačuvano", f"Fajl sačuvan:\n{path}")

    def _play_modified(self):
        if self.modified:
            self.play(self.modified[0], self.modified[1])

    def play(self, sig, fs):
        if sig is None:
            return
        self._update_state(State.PLAYING)
        threading.Thread(target=lambda: sd.play(sig.astype(np.float32), int(fs)), daemon=True).start()

    def stop(self):
        self._update_state(State.MODIFIED if self.modified else State.LOADED)
        sd.stop()