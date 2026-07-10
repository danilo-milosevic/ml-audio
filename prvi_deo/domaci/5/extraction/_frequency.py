import librosa

def extract_spectral_centroid(signal, sr, n_fft, hop_length, win_length, **kwargs):
    return librosa.feature.spectral_centroid(y=signal, sr=sr, n_fft=n_fft, hop_length=hop_length, win_length=win_length)

def extract_spectral_bandwith(signal, sr, n_fft, hop_length, win_length, **kwargs):
    return librosa.feature.spectral_bandwidth(y=signal, sr=sr, n_fft=n_fft, hop_length=hop_length, win_length=win_length)

def extract_spectral_rolloff(signal, sr, n_fft, hop_length, win_length, **kwargs):
    return librosa.feature.spectral_rolloff(y=signal, sr=sr, n_fft=n_fft, hop_length=hop_length, win_length=win_length)