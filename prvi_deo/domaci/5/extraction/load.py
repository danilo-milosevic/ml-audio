import numpy as np
from scipy.io import wavfile

from extraction.consts import INT16_MAX, INT32_MAX, UINT8_MAX
def load_wav_as_float(path):
    fs, data = wavfile.read(path)
    data_type = data.dtype
    data = data.astype(np.float64)
 
    match data_type:
        case np.int16:
            bits = 16
            sig = data / float(INT16_MAX)
        case np.int32:
            bits = 32
            sig = data / float(INT32_MAX)
        case np.uint8:
            bits = 8
            sig = (data - float(UINT8_MAX)) / float(UINT8_MAX)
        case np.float32, np.float64:
            bits = 32
            sig = data / (np.max(np.abs(data)) or 1.0)
        case _:
            bits = 16
            sig = data / (np.max(np.abs(data)) or 1.0)
 
    if sig.ndim > 1:
        sig = sig.mean(axis=1)
 
    return fs, sig, bits