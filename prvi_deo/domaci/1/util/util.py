import numpy as np
from consts.consts import INT16_MAX

def spectrum_db(sig, fs):
    n = len(sig)
    win = np.hanning(n)
    spec = np.fft.rfft(sig * win)
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    mag = np.abs(spec) + 1e-12
    mag_db = 20 * np.log10(mag / np.max(mag))
    return freqs, mag_db


def to_int16(sig):
    sig = np.clip(sig, -1.0, 1.0)
    return (sig * INT16_MAX).astype(np.int16)
