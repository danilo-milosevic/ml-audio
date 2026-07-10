import numpy as np
import librosa

def extract_amplitude_envelope(signal, frame_length = 1024, hop_length = 512, **kwargs):
    return np.array([
        max(np.abs(signal[i: i+frame_length]))
        for i in range(0, len(signal), hop_length)
    ])

def extract_rms(signal, frame_length=1024, hop_length=512, **kwargs):
    return librosa.feature.rms(y=signal, frame_length=frame_length, hop_length=hop_length)

def extract_zero_crossing_rate(signal, sr, **kwargs):
    zcrs = librosa.feature.zero_crossing_rate(y=signal)
    return zcrs, sum(librosa.zero_crossings(y=signal))