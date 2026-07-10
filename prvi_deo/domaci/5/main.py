from extraction import get_features, plot_features, load_wav_as_float
from pathlib import Path
import numpy as np


SCRIPT_DIR = Path(__file__).resolve().parent
PATHS = ["music.wav", "factory.wav"]
segments = {}
sr = None

for path in PATHS:
    sr1, segments[path], _ = load_wav_as_float(SCRIPT_DIR / path)
    if sr is None:
        sr = sr1
    elif sr1 != sr:
        raise ValueError("Sample rates have to be equal")


composed = np.concatenate(list(segments.values()))

durations = [len(segments[path]) / sr for path in PATHS]
cumulative = np.cumsum(durations)
boundaries = [
    (cumulative[i], PATHS[i + 1])
    for i in range(len(PATHS) - 1)
]

features = get_features(composed, sr, n_fft=1024, hop_length=512, win_length=1024)
plot_features(features, sr, hop_length=512, boundaries=boundaries, ncols=3)