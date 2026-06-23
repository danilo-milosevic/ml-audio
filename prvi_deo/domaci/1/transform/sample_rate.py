from scipy import signal as sps

def change_sample_rate(sig, fs_in, fs_out):
    from math import gcd
    fs_in_i = int(round(fs_in))
    fs_out_i = int(round(fs_out))
    g = gcd(fs_in_i, fs_out_i)
    up = fs_out_i // g
    down = fs_in_i // g
    out = sps.resample_poly(sig, up, down)
    return out
