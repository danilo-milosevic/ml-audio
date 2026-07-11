import librosa


def extract_chroma(signal, sr, n_fft, hop_length, win_length, **kwargs):
    return librosa.feature.chroma_stft(y=signal, sr=sr, n_fft=n_fft, hop_length=hop_length, win_length=win_length)