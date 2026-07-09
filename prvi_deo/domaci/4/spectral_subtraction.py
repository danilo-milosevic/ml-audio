import numpy as np
from scipy.signal import get_window, spectrogram, istft


class SpectralSubtraction:
    def __init__(
        self,
        apriori_SNR=1,
        alpha=0.05,
        beta1=0.5,
        beta2=1,
        lam=3,
        nfft=1024,
        window_duration=0.031,
        overlap_ratio=0.45,
        t_min=0.4,
        t_max=1.0,
    ):
        self.apriori_SNR = apriori_SNR
        self.alpha = alpha
        self.beta1 = beta1
        self.beta2 = beta2
        self.lam = lam
        self.nfft = nfft
        self.window_duration = window_duration
        self.overlap_ratio = overlap_ratio
        self.t_min = t_min
        self.t_max = t_max

    def __call__(self, signal, fs):
        return self.denoise(signal, fs)

    def denoise(self, signal, fs):
        x = np.asarray(signal, dtype=np.float64)
        if x.ndim > 1:
            x = x[:, 0]

        window_length = int(round(self.window_duration * fs))
        window = get_window("hamming", window_length)
        overlap = int(self.overlap_ratio * window_length)

        nfft = max(self.nfft, self.window_duration * fs)
        f, t, S = spectrogram(
            x,
            fs=fs,
            window=window,
            nperseg=window_length,
            noverlap=overlap,
            nfft=nfft,
            mode="complex",
        )

        t_index = np.where((t > self.t_min) & (t < self.t_max))[0]

        S_noise = np.abs(S[:, t_index]) ** 2
        noise_spectrum = np.mean(S_noise, axis=1, keepdims=True)
        noise_specgram = np.repeat(noise_spectrum, S.shape[1], axis=1)

        absS = np.abs(S) ** 2
        SNR_est = np.maximum((absS / (noise_specgram + 1e-12)) - 1, 0)

        if self.apriori_SNR == 1:
            for i in range(1, SNR_est.shape[1]):
                SNR_est[:, i] = (1 - self.alpha) * SNR_est[:, i] + self.alpha * SNR_est[:, i - 1]

        attenuation = np.maximum(
            (1 - self.lam * ((1 / (SNR_est + 1)) ** self.beta1)) ** self.beta2,
            0,
        )

        STFT_denoised = attenuation * S

        _, output_signal = istft(
            STFT_denoised,
            fs=fs,
            window=window,
            nperseg=window_length,
            noverlap=overlap,
            nfft=nfft,
            input_onesided=False,
        )

        output_signal = np.real(output_signal)
        output_signal = output_signal / (np.max(np.abs(output_signal)) + 1e-12)

        return output_signal.astype(np.float32)
