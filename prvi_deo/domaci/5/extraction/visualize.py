import numpy as np
import matplotlib.pyplot as plt
import librosa.display

from extraction.extract import FeatureTypes

_2D_FEATURES = {
    FeatureTypes.MFCC,
    FeatureTypes.CHROMA,
    FeatureTypes.SPECTROGRAM,
    FeatureTypes.TEMPOGRAM,
}

_SPECSHOW_YAXIS = {
    FeatureTypes.MFCC: None,
    FeatureTypes.CHROMA: 'chroma',
    FeatureTypes.SPECTROGRAM: 'mel',
    FeatureTypes.TEMPOGRAM: 'tempo',
}


def _to_feature_type(feature):
    return feature if isinstance(feature, FeatureTypes) else FeatureTypes(feature)


def _to_1d(array):
    return np.asarray(array).squeeze()


def _plot_1d(ax, values, sr, hop_length, title):
    values = _to_1d(values)
    t = librosa.frames_to_time(np.arange(len(values)), sr=sr, hop_length=hop_length)
    ax.plot(t, values)
    ax.set_title(title)
    ax.set_xlabel("Vreme (s)")
    ax.set_ylabel("Vrednost")
    if len(t):
        ax.set_xlim([t.min(), t.max()])


def _plot_2d(ax, matrix, sr, hop_length, title, y_axis):
    matrix = np.asarray(matrix)
    img = librosa.display.specshow(
        matrix, sr=sr, hop_length=hop_length,
        x_axis='time', y_axis=y_axis, ax=ax
    )
    ax.set_title(title)
    return img


def _plot_boundaries(ax, boundaries):
    for b in boundaries:
        time, label = b if isinstance(b, (tuple, list)) else (b, None)
        ax.axvline(time, color='k', linestyle='--', alpha=0.7)
        if label:
            trans = ax.get_xaxis_transform()
            ax.text(
                time, -0.08, f" {label}",
                transform=trans, rotation=0,
                va='top', ha='left', fontsize=8, color='k',
                clip_on=False
            )


def plot_features(extracted_features, sr, hop_length=512, features=None,
                   boundaries=None, figsize=(9, 4), hspace=1.0, ncols=2):
    features = features or list(extracted_features.keys())
    nrows = int(np.ceil(len(features) / ncols))

    fig, axes = plt.subplots(
        nrows, ncols,
        figsize=(figsize[0] * ncols, figsize[1] * nrows)
    )
    axes = np.atleast_1d(axes).flatten()

    for ax, feature in zip(axes, features):
        feature_type = _to_feature_type(feature)
        data = extracted_features[feature]
        title = feature_type.value.replace('_', ' ').capitalize()

        if feature_type == FeatureTypes.ZERO_CROSSING_RATE:
            zcrs, total = data
            _plot_1d(ax, zcrs, sr, hop_length, f"{title} (ukupno prelaza: {total})")
        elif feature_type in _2D_FEATURES:
            _plot_2d(ax, data, sr, hop_length, title, _SPECSHOW_YAXIS.get(feature_type))
        else:
            _plot_1d(ax, data, sr, hop_length, title)

        if boundaries:
            _plot_boundaries(ax, boundaries)

    for ax in axes[len(features):]:
        ax.axis('off')

    plt.tight_layout()
    fig.subplots_adjust(hspace=hspace, wspace=0.3)
    plt.show()