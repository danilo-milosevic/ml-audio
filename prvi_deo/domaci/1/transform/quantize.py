import numpy as np

def quantize_bits(sig, n_bits):
    n_bits = int(n_bits)
    levels = 2 ** n_bits
    sig_c = np.clip(sig, -1.0, 1.0)
    q = np.round((sig_c + 1.0) / 2.0 * (levels - 1))
    q = q / (levels - 1) * 2.0 - 1.0
    return q