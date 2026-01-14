from abc import ABC, abstractmethod

import numpy as np


class _NodeComplexCPU(ABC):
    """
    A node that is made by applying different nodes. It
    is different than the other nodes because it needs
    to import different nodes to process the input(s).

    This is the equivalent to `_NodeComplexGPU` of 
    `yta-editor-nodes-gpu`, but in CPU.

    TODO: This is, by now, just a class to identify these
    new type of nodes.
    """

    @abstractmethod
    def process(
        self,
        input: np.ndarray,
        **kwargs
    ) -> np.ndarray:
        pass

"""
Specific implementations start below this class.
"""

class DisplayOverAtNodeComplexCPU(_NodeComplexCPU):
    """
    The overlay input is placed in the scene with the
    given position, rotation and size, and then put as
    an overlay of the also given base input.

    Information:
    - The scene size is `(1920, 1080)`, so provide the
    `position` parameter according to it, where it is
    representing the center of the texture.
    - The `rotation` is in degrees, where `rotation=90`
    means rotating 90 degrees to the right.
    - The `size` parameter must be provided according to
    the previously mentioned scene size `(1920, 1080)`.

    TODO: This has no inheritance, is special and we need
    to be able to identify it as a valid one.

    TODO: This must be implemented
    """

    def process(
        self,
        input: np.ndarray,
        **kwargs
    ) -> np.ndarray:
        raise NotImplementedError('Not implemented yet')