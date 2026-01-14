"""
The nodes that modify inputs by using static parameters
and not 't' time moments, with CPU.
"""
from yta_programming.singleton import SingletonABCMeta
from yta_editor_utils.texture import TextureUtils
from abc import abstractmethod
from typing import Union

import numpy as np


# TODO: Move this abstract classes and reorganize
# the modules because we have only one 'processor'
# class but the module is called like that...
class _NodeProcessorCPU(metaclass = SingletonABCMeta):
    """
    *Singleton class*

    *For internal use only*

    Class to represent a node processor that uses CPU
    to transform the input.

    This class must be implemented by any processor
    that uses CPU to modify an input.
    """

    def __init__(
        self,
        **kwargs
    ):
        pass

    def __reinit__(
        self,
        **kwargs
    ):
        pass
    
    # TODO: Just code and the same attributes that the
    # GPU version also has
    @abstractmethod
    def process(
        self,
        # TODO: What about the type (?)
        input: np.ndarray,
        **kwargs
    # TODO: What about the output type (?)
    ) -> np.ndarray:
        """
        Process the provided 'input' and transform it by
        using the code that is defined here.
        """
        # TODO: Specific attributes can be received as
        # **kwargs to modify the specific process
        pass

"""
Specific implementations start below this class.
"""

class SelectionMaskProcessorCPU(_NodeProcessorCPU):
    """
    Class to use a mask selection (from which we will
    determine if the pixel must be applied or not) to
    apply the `processed_input` on the `original_input`.
    """

    def process(
        self,
        # TODO: What about the type (?)
        original_input: np.ndarray,
        processed_input: np.ndarray,
        selection_mask_input: np.ndarray
    ):
        """
        Apply the `selection_mask` provided to the also
        given `original` and `processed` nuumpy arrays to
        obtain the processed one but affected only as the
        selection mask says.

        The input are processed as float32, with float 
        precission, to be able to calculate properly,
        and then returned to uint8 [0, 255] values (the
        ones our OpenGL is able to handle with the 'f1'
        dtype and the sampler2d uniforms).
        """
        # We force to have float precission for the calculations
        original_input = TextureUtils.numpy_to_float32(original_input)
        processed_input = TextureUtils.numpy_to_float32(processed_input)
        selection_mask_input = TextureUtils.numpy_to_float32(selection_mask_input)

        # We need a 3D or 4D mask
        selection_mask_input = (
            np.expand_dims(selection_mask_input, axis = -1)
            if selection_mask_input.ndim == 2 else
            selection_mask_input
        )

        selection_mask_input = (
            np.repeat(
                a = selection_mask_input,
                repeats = original_input.shape[-1],
                axis = -1
            )
            if (
                selection_mask_input.shape[-1] == 1 and
                original_input.shape[-1] in (3, 4)
            ) else
            selection_mask_input
        )

        # Mix with the selection mask
        final = original_input * (1.0 - selection_mask_input) + processed_input * selection_mask_input

        return TextureUtils.numpy_to_uint8(final)
    
# TODO: Just for testing, at least by now
class ColorContrastNodeProcessorCPU(_NodeProcessorCPU):
    """
    Node processor to modify the color contrast of the
    input.

    Depending on the factor:
    - `factor>1.0` = More contrast
    - `factor==1.0` = Same contrast
    - `factor<1.0` = Less contrast

    TODO: Improve this, its just temporary
    """

    def __init__(
        self,
        factor: float = 1
    ):
        self.factor: float = factor
        """
        The factor to apply to change the color contrast.
        """

    def __reinit__(
        self,
        factor: Union[float, None] = None
    ):
        if factor is not None:
            self.factor = factor

    def process(
        self,
        input: np.ndarray,
        # TODO: Maybe add 'factor' also here that can be None
        # to use the original of the instance
        **kwargs
    ):
        # Ensure float32 [0, 1]
        source = TextureUtils.numpy_to_float32(input)

        # We do this to be the same as in GPU but it
        # should be calculated... and also for the GPU
        mean = np.array([0.5, 0.5, 0.5, 0.5], dtype = np.float32)

        # mean = input.mean(
        #     axis = (0, 1),
        #     keepdims = True
        # )
        """
        factor > 1 -> More contrast
        factor < 1 -> Less contrast
        """
        out = (source - mean) * self.factor + mean
        out = np.clip(out, 0, 1)

        return out
    
class BrightnessNodeProcessorCPU(_NodeProcessorCPU):
    """
    Node processor to modify the brightness of the
    input by multiplying it by a factor.

    Depending on the factor:
    - `factor>1.0` = Lighter
    - `factor==1.0` = Same brightness
    - `factor<1.0` = Darker
    """

    def __init__(
        self,
        factor: float = 1
    ):
        self.factor: float = factor
        """
        The factor to apply to change the brightness.
        """

    def __reinit__(
        self,
        factor: Union[float, None] = None
    ):
        if factor is not None:
            self.factor = factor

    def process(
        self,
        input: np.ndarray,
        # TODO: Maybe add 'factor' also here that can be None
        # to use the original of the instance
        **kwargs
    ):
        """
        The `input` must be `float32` and the output will
        be also `float32`.
        """
        # Ensure float32 [0, 1]
        source = TextureUtils.numpy_to_float32(input)

        # Copy to avoid mutating upstream buffers
        output = source.copy()

        # Apply brightness (RGB only)
        output[..., :3] *= self.factor

        # Clamp
        output = np.clip(output, 0.0, 1.0)

        return output
    
class BlackAndWhiteNodeProcessorCPU(_NodeProcessorCPU):
    """
    Node processor to test the color contrast
    change.

    TODO: Improve this, its just temporary
    """

    def process(
        self,
        input: np.ndarray,
        **kwargs
    ) -> np.ndarray:
        """
        The `input` must be `float32` and the output will
        be also `float32`.
        """
        # Ensure float32 [0, 1]
        source = TextureUtils.numpy_to_float32(input)

        # Standard luminance conversion Rec.709
        gray = 0.2126 * source[..., 0] + 0.7152 * source[..., 1] + 0.0722 * source[..., 2]
        gray = np.clip(gray, 0, 1)

        return np.dstack(
            [gray, gray, gray, input[..., 3]]
            if input.shape[-1] == 4 else
            [gray, gray, gray]
        )
    
