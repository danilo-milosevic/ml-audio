import numpy as np
from scipy.fftpack import fft, ifft
import scipy.signal as sg


def halfwave_rectification(array):
    halfwave = np.zeros(array.size)
    halfwave[np.argwhere(array > 0)] = 1
    return halfwave


class Wiener:
    """
    Wiener filtering based on the article "Improved Signal-to-Noise Ratio Estimation for Speech
    Enhancement".

    Reference:
        Cyril Plapous, Claude Marro, Pascal Scalart. Improved Signal-to-Noise Ratio Estimation for Speech
        Enhancement. IEEE Transactions on Audio, Speech and Language Processing, 2006.
    """

    def __init__(self, signal, fs, t_noise_start=0.0, t_noise_end=1.0):
        self.FS = fs
        self.x = np.asarray(signal, dtype=np.float64)
        if self.x.ndim > 1:
            self.x = self.x.mean(axis=1)

        self.NFFT = 2 ** 10
        self.SHIFT = 0.5
        self.FRAME = int(0.02 * self.FS)
        self.OFFSET = int(self.SHIFT * self.FRAME)

        self.WINDOW = sg.windows.hann(self.FRAME)
        self.EW = np.sum(self.WINDOW)

        self.N_NOISE = int(t_noise_start * self.FS), int(t_noise_end * self.FS)

        length = self.x.size
        self.frames = np.arange((length - self.FRAME) // self.OFFSET + 1)

        self.Sbb = self.welchs_periodogram()

    @staticmethod
    def a_posteriori_gain(SNR):
        return (SNR - 1) / SNR

    @staticmethod
    def a_priori_gain(SNR):
        return SNR / (SNR + 1)

    def welchs_periodogram(self):
        Sbb = np.zeros(self.NFFT)
        n_start, n_end = self.N_NOISE
        noise_frames = np.arange(((n_end - n_start) - self.FRAME) // self.OFFSET + 1)
        for frame in noise_frames:
            i_min = frame * self.OFFSET + n_start
            i_max = i_min + self.FRAME
            x_framed = self.x[i_min:i_max] * self.WINDOW
            X_framed = fft(x_framed, self.NFFT)
            Sbb = frame * Sbb / (frame + 1) + np.abs(X_framed) ** 2 / (frame + 1)
        return Sbb

    def wiener(self):
        s_est = np.zeros(self.x.shape)
        for frame in self.frames:
            i_min, i_max = frame * self.OFFSET, frame * self.OFFSET + self.FRAME
            x_framed = self.x[i_min:i_max] * self.WINDOW
            X_framed = fft(x_framed, self.NFFT)

            SNR_post = (np.abs(X_framed) ** 2 / self.EW) / self.Sbb
            G = Wiener.a_priori_gain(SNR_post)
            S = X_framed * G

            temp_s_est = np.real(ifft(S)) * self.SHIFT
            s_est[i_min:i_max] += temp_s_est[:self.FRAME]

        s_est = s_est / (np.max(np.abs(s_est)) + 1e-12)
        return s_est.astype(np.float32)

    def wiener_two_step(self):
        beta = 0.98
        s_est_tsnr = np.zeros(self.x.shape)
        S = np.zeros((2, self.NFFT), dtype="complex128")

        for frame in self.frames:
            i_min, i_max = frame * self.OFFSET, frame * self.OFFSET + self.FRAME
            x_framed = self.x[i_min:i_max] * self.WINDOW
            X_framed = fft(x_framed, self.NFFT)

            SNR_post = np.abs(X_framed) ** 2 / self.EW / self.Sbb
            G = Wiener.a_priori_gain(SNR_post)
            S[0, :] = G * X_framed

            SNR_dd_prio = beta * np.abs(S[-1, :]) ** 2 / self.Sbb + (1 - beta) * halfwave_rectification(
                SNR_post - 1
            )
            G_dd = Wiener.a_priori_gain(SNR_dd_prio)
            S_dd = G_dd * X_framed

            SNR_tsnr_prio = np.abs(S_dd) ** 2 / self.Sbb
            G_tsnr = Wiener.a_priori_gain(SNR_tsnr_prio)
            S_tsnr = G_tsnr * X_framed

            temp_s_est_tsnr = np.real(ifft(S_tsnr)) * self.SHIFT
            s_est_tsnr[i_min:i_max] += temp_s_est_tsnr[:self.FRAME]

            S = np.roll(S, 1, axis=0)

        s_est_tsnr = s_est_tsnr / (np.max(np.abs(s_est_tsnr)) + 1e-12)
        return s_est_tsnr.astype(np.float32)

    def denoise(self, method="two_step"):
        if method == "two_step":
            return self.wiener_two_step()
        return self.wiener()
