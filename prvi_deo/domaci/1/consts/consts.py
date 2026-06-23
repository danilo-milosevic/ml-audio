import numpy as np

INT16_MAX = max(np.iinfo(np.int16).max, abs(np.iinfo(np.int16).min))
INT32_MAX = max(np.iinfo(np.int32).max, abs(np.iinfo(np.int32).min))
UINT8_MAX = max(np.iinfo(np.uint8).max, abs(np.iinfo(np.uint8).min))