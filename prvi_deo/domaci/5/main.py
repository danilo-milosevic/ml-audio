from extraction import get_features, plot_features, load_wav_as_float
from pathlib import Path
import numpy as np
import random

from scipy.io.wavfile import write

SCRIPT_DIR = Path(__file__).resolve().parent
RESULT_DIR = SCRIPT_DIR / "results"
PATHS = [
    "city_noise.wav", 
    "factory.wav",
    "guitar.wav",
    "piano.wav",
    "rap_drums.wav",
    "slow.wav",
    "voice.wav"
]
random.shuffle(PATHS)
MAX_LENGTH_S = 5
TARGET_SR = 48000

MAX_SAMPLES = int(TARGET_SR * MAX_LENGTH_S)
segments = {}

for path in PATHS:
    sr, signal, _ = load_wav_as_float(SCRIPT_DIR / path)
    if sr != TARGET_SR:
        raise ValueError(f"All recordings need to be sampled with {TARGET_SR}Hz")
    
    start = int(random.random() * (len(signal) - MAX_SAMPLES))
    segments[path] = signal[start:start + MAX_SAMPLES]


composed = np.concatenate(list(segments.values()))
write(
    RESULT_DIR / "composed.wav",
    TARGET_SR,
    (composed * 32767).astype(np.int16)
)

durations = [len(segments[path]) / sr for path in PATHS]
cumulative = np.concatenate(([0], np.cumsum(durations)))
boundaries = [
    (cumulative[i], PATHS[i])
    for i in range(len(PATHS))
]

features = get_features(composed, sr, n_fft=1024, hop_length=512, win_length=1024)
plot_features(features, sr, hop_length=512, boundaries=boundaries, ncols=2, save_path=RESULT_DIR)