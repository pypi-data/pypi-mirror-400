import numpy as np

#%% NORMALIZATION

def minmax_normalize(array, minimum=None, maximum=None, symmetric=False):
    if minimum is None: minimum = np.min(array)
    if maximum is None: maximum = np.max(array)
    if symmetric: return array * 2 / (maximum - minimum)
    return (array - minimum) / (maximum - minimum)

def invert_minmax_normalize(array, minimum, maximum):
    return array*(maximum - minimum) + minimum

#%% QUANTIZATION

def round_and_clip(array, minimum=None, maximum=None, dtype=np.float32):
    """Rounds up values in an array, limiting values to [min, max]"""
    if minimum is None: minimum = np.min(array)
    if maximum is None: maximum = np.max(array)
    return np.clip(array.round(), minimum, maximum).astype(dtype)

#%% INTERPOLATION

def sinc_interpolation(signal, interpolation_factor):
  """Credit to Oliver Neill, 2024"""

  # Get Fourier transform
  N = len(signal)
  fourier = np.fft.fft(signal, norm="ortho")

  # Pad Fourier transform with zeroes
  fourier_2 = np.pad(fourier, [0, (interpolation_factor-1)*N])

  # Transform back from Fourier space
  signal_2 = np.fft.ifft(fourier_2, norm="ortho")
  
  return np.sqrt(interpolation_factor)*signal_2 # renormalise