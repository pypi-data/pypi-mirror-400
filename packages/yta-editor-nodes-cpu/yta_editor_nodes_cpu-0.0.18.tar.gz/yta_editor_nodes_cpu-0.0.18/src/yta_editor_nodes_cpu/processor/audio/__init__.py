"""
When working with audio frames, we don't need
to use the GPU because audios are 1D and the
information can be processed perfectly with
a library like numpy.

If we need a very intense calculation for an
audio frame (FFT, convolution, etc.) we can
use CuPy or some DPS specific libraries, but
90% is perfectly done with numpy.

If you want to modify huge amounts of audio
(some seconds at the same time), you can use
CuPy, that has the same API as numpy but
working in GPU. Doing this below most of the
changes would work:
- `import numpy as np` → `import cupy as np`
"""
from abc import ABC, abstractmethod

import numpy as np


class _AudioNodeProcessor(ABC):
    """
    Base audio node class to implement a
    change in an audio frame by using the
    numpy library.
    """

    @abstractmethod
    def process(
        self,
        input: np.ndarray,
        t: float
    ) -> np.ndarray:
        """
        Process the provided audio 'input' that
        is played on the given 't' time moment.
        """
        pass


class VolumeAudioNodeProcessor(_AudioNodeProcessor):
    """
    Set the volume.

    TODO: Explain properly.
    """

    def __init__(
        self,
        factor_fn
    ):
        """
        factor_fn: function (t, index) -> factor volumen
        """
        self.factor_fn: callable = factor_fn

    def process(
        self,
        input: np.ndarray,
        t: float
    ) -> np.ndarray:
        """
        Process the provided audio 'input' that
        is played on the given 't' time moment.
        """
        factor = self.factor_fn(t, 0)

        samples = input
        samples *= factor

        # Determine dtype according to format
        # samples = (
        #     samples.astype(np.int16)
        #     # 'fltp', 's16', 's16p'
        #     if 's16' in input.format.name else
        #     samples.astype(np.float32)
        # )

        return samples

__all__ = [
    'VolumeAudioNodeProcessor',
]