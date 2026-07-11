from extraction import _frequency, _perception, _temporal, _time
from enum import Enum

class FeatureTypes(Enum):
    AMPLITUDE_ENVELOPE = 'amplitude_envelope'
    CHROMA = 'chroma'
    ONSET_STRENGTH = 'onset_strength'
    RMS = 'rms'
    SPECTRAL_BANDWITH = 'spectral_bandwith'
    SPECTRAL_CENTROID = 'spectral_centroid'
    SPECTRAL_ROLLOFF  = 'spectral_roloff'
    TEMPOGRAM = 'tempogram'
    ZERO_CROSSING_RATE = 'zero_crossing_rate'

DEFAULT_FEATURES = [feature_type.value for feature_type in FeatureTypes]

FEATURE_EXTRACTORS = {
    FeatureTypes.AMPLITUDE_ENVELOPE: _time.extract_amplitude_envelope,
    FeatureTypes.CHROMA: _perception.extract_chroma,
    FeatureTypes.ONSET_STRENGTH: _temporal.extract_onset_strength,
    FeatureTypes.RMS: _time.extract_rms,
    FeatureTypes.SPECTRAL_BANDWITH: _frequency.extract_spectral_bandwith,
    FeatureTypes.SPECTRAL_CENTROID: _frequency.extract_spectral_centroid,
    FeatureTypes.SPECTRAL_ROLLOFF: _frequency.extract_spectral_rolloff,
    FeatureTypes.TEMPOGRAM: _temporal.extract_tempogram,
    FeatureTypes.ZERO_CROSSING_RATE: _time.extract_zero_crossing_rate
}

class StdLogger:
    def log(self, msg):
        print(msg)

class NoopLogger:
    def log(self, msg):
        pass
        
        
def get_features(signal, sr, features = DEFAULT_FEATURES, verbose = True, **kwargs):
    extracted_features = {}
    logger = StdLogger() if verbose else NoopLogger()

    for feature in features:
        logger.log(f"Extracting {feature}...")
        extractor = FEATURE_EXTRACTORS.get(FeatureTypes(feature), None)
        if extractor is None:
            raise ValueError(f"Unknown extractor for feature {feature}")
        extracted_features[feature] = extractor(signal, sr, **kwargs)
        logger.log(f"\t Extracted!")
    
    return extracted_features
