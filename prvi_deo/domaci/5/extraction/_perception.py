import librosa

def extract_mfcc(signal, sr, **kwargs):
    return librosa.feature.mfcc(y=signal, sr=sr)

def extract_chroma(signal, sr, n_fft, hop_length, win_length, **kwargs):
    return librosa.feature.chroma_stft(y=signal, sr=sr, n_fft=n_fft, hop_length=hop_length, win_length=win_length)

def extract_spectrogram(signal, sr, n_fft, hop_length, win_length, **kwargs):
    return librosa.feature.melspectrogram(y=signal, sr=sr, n_fft=n_fft, hop_length=hop_length, win_length=win_length)