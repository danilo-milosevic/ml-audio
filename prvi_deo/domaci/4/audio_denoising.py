from abc import ABC, abstractmethod
from pathlib import Path
from enum import Enum
import wiener as w
import spectral_subtraction as ss

import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from scipy.signal import stft

class ScheduleFields(Enum):
    ORIGINAL = 'original'
    NOISY = 'noisy'
    AUDACITY_DENOISED = 'audacity_denoised'
    METHOD = 'method'

SCRIPT_DIR = Path(__file__).resolve().parent

MUSIC_FILES = {
    ScheduleFields.ORIGINAL: "music/music.wav",
    ScheduleFields.NOISY: "music/music_white.wav",
    ScheduleFields.AUDACITY_DENOISED: "music/music_white_denoise.wav",
}

SPEECH_FILES = {
    ScheduleFields.ORIGINAL: "speech/logatomi.wav",
    ScheduleFields.NOISY: "speech/logatomi_white.wav",
    ScheduleFields.AUDACITY_DENOISED: "speech/logatomi_white_denoise.wav",
}

OUTPUT_DIR = "output"

N_FFT = 1024
HOP_LENGTH = N_FFT // 4

def load_audio(path, target_sr = None):
    if not path.exists():
        raise FileNotFoundError(f"Fajl nije pronadjen: {path}")

    signal, sr = sf.read(str(path))

    if signal.ndim > 1:
        signal = signal.mean(axis=1)

    if target_sr is not None and target_sr != sr:
        raise NotImplementedError(
            "Resample nije implementiran u ovom skeletu -- ucitaj fajl sa "
            "originalnom frekvencijom ili dodaj resample logiku."
        )

    return signal.astype(np.float32), sr


def save_audio(path, signal, sr) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), signal, sr)


def compute_spectrogram(signal, sr, n_fft, hop_length):
    noverlap = n_fft - hop_length
    f, t, Zxx = stft(signal, fs=sr, nperseg=n_fft, noverlap=noverlap)
    return f, t, Zxx


def magnitude_db(Zxx, eps= 1e-10):
    return 20 * np.log10(np.abs(Zxx) + eps)


class Denoiser(ABC):
    name: str = "BaseDenoiser"

    @abstractmethod
    def denoise(self, signal, sr):
        raise NotImplementedError

    def __call__(self, signal, sr):
        return self.denoise(signal, sr)


class IdentityDenoiser(Denoiser):
    name = "Identity"

    def denoise(self, signal, sr):
        return signal.copy()

class WienerDenoiser(Denoiser):
    name = "Wiener"

    def denoise(self, signal, sr):
        noised_audio = w.Wiener(signal = signal, fs = sr)
        return noised_audio.wiener()
    
class SpectralSubtractionDenoiser(Denoiser):
    name = "SpectralSubtractionDenoiser"

    def __init__(self, **kwargs):
        self._ss = ss.SpectralSubtraction(**kwargs)

    def denoise(self, signal, sr):
        return self._ss.denoise(signal, sr)

def compare_spectrograms(
    original,
    denoised,
    sr,
    title = "",
    n_fft = N_FFT,
    hop_length = HOP_LENGTH,
    save_path = None,
):
    f, t, Z_orig = compute_spectrogram(original, sr, n_fft, hop_length)
    _, _, Z_den = compute_spectrogram(denoised, sr, n_fft, hop_length)

    mag_orig_db = magnitude_db(Z_orig)
    mag_den_db = magnitude_db(Z_den)

    n_freq = min(mag_orig_db.shape[0], mag_den_db.shape[0])
    n_time = min(mag_orig_db.shape[1], mag_den_db.shape[1])
    mag_orig_db = mag_orig_db[:n_freq, :n_time]
    mag_den_db = mag_den_db[:n_freq, :n_time]
    f = f[:n_freq]
    t = t[:n_time]

    diff_db = mag_orig_db - mag_den_db

    fig, axes = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

    im0 = axes[0].pcolormesh(t, f, mag_orig_db, shading="auto", cmap="magma")
    axes[0].set_title(f"{title} -- originalni signal")
    axes[0].set_ylabel("Frekvencija [Hz]")
    fig.colorbar(im0, ax=axes[0], label="dB")

    im1 = axes[1].pcolormesh(t, f, mag_den_db, shading="auto", cmap="magma")
    axes[1].set_title(f"{title} -- denoised signal")
    axes[1].set_ylabel("Frekvencija [Hz]")
    fig.colorbar(im1, ax=axes[1], label="dB")

    vmax = np.max(np.abs(diff_db))
    im2 = axes[2].pcolormesh(
        t, f, diff_db, shading="auto", cmap="coolwarm", vmin=-vmax, vmax=vmax
    )
    axes[2].set_title(f"{title} -- razlika (original - denoised) [dB]")
    axes[2].set_ylabel("Frekvencija [Hz]")
    axes[2].set_xlabel("Vreme [s]")
    fig.colorbar(im2, ax=axes[2], label="dB razlika")

    fig.tight_layout()

    if save_path is not None:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=150)
        print(f"  Sacuvan grafik: {save_path}")

    plt.show()
    plt.close(fig)


def process_file(original_path, noisy_path, denoiser):
    original_signal, sr = load_audio(SCRIPT_DIR / original_path)
    noisy_signal, _ = load_audio(SCRIPT_DIR / noisy_path)
    denoised_signal = denoiser(noisy_signal, sr)

    out_path = SCRIPT_DIR / OUTPUT_DIR / f"{original_path}_{denoiser.name.replace(' ', '_')}.wav"
    save_audio(out_path, denoised_signal, sr)

    fig_path = SCRIPT_DIR / OUTPUT_DIR / f"{original_path}_{denoiser.name.replace(' ', '_')}_spectrograms.png"
    compare_spectrograms(
        original_signal, denoised_signal, sr, title=f"{original_path} [{denoiser.name}]", save_path=fig_path
    )


def main() -> None:
    schedules = [
        (MUSIC_FILES[ScheduleFields.ORIGINAL], MUSIC_FILES[ScheduleFields.NOISY], WienerDenoiser()),
        (MUSIC_FILES[ScheduleFields.ORIGINAL], MUSIC_FILES[ScheduleFields.NOISY], SpectralSubtractionDenoiser()),
        (MUSIC_FILES[ScheduleFields.ORIGINAL], MUSIC_FILES[ScheduleFields.AUDACITY_DENOISED], IdentityDenoiser()),
        (SPEECH_FILES[ScheduleFields.ORIGINAL], SPEECH_FILES[ScheduleFields.NOISY], WienerDenoiser()),
        (SPEECH_FILES[ScheduleFields.ORIGINAL], SPEECH_FILES[ScheduleFields.NOISY], SpectralSubtractionDenoiser()),
        (SPEECH_FILES[ScheduleFields.ORIGINAL], SPEECH_FILES[ScheduleFields.AUDACITY_DENOISED], IdentityDenoiser()),
    ]

    for (original_path, noisy_path, denoiser) in schedules:
        process_file(original_path, noisy_path, denoiser)


if __name__ == "__main__":
    main()
