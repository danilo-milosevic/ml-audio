import librosa

def extract_onset_strength(signal, sr, hop_length, **kwargs):
    return librosa.onset.onset_strength(y=signal, sr=sr, hop_length=hop_length)

def extract_tempogram(signal, sr, hop_length, **kwargs):
    oenv = extract_onset_strength(signal=signal, sr=sr, hop_length=hop_length)
    return librosa.feature.tempogram(onset_envelope=oenv, sr=sr,
                                        hop_length=hop_length)