"""
We don't name it 'blend' instead of 'process' because
the GPU classes have the 'process' name due to the
inheritance from OpenGL classes, and we want to avoid
misunderstandings.
"""
# TODO: Should we keep this functionality (?)
# from yta_video_opengl.utils import texture_to_frame
from yta_editor_nodes_cpu.blender.utils import _validate_inputs_and_mix_weights, _ensure_uint8
from yta_editor_utils.texture import TextureUtils
from yta_programming.singleton import SingletonABCMeta
from yta_validation.parameter import ParameterValidator
from abc import abstractmethod
from typing import Union

import numpy as np


class _BlenderCPU(metaclass = SingletonABCMeta):
    """
    *Singleton class*

    *For internal use only*

    Class to represent a blender that uses CPU to
    blend the inputs.

    This class must be implemented by any blender
    that uses CPU to blend inputs.
    """

    @abstractmethod
    def _blend(
        self,
        base_input: np.ndarray,
        overlay_input: np.ndarray,
        **kwargs
    # TODO: Is this the expected type (?)
    # TODO: What about OpenGL textures (?)
    ) -> np.ndarray:
        """
        *For internal use only*

        *This method must be overwritten by the specific
        classes*

        The internal process to blend and mix the provided
        `base_input` and `overlay_input`.

        This method should not force uint8 nor [0, 255]
        range by itself as it would be done in the 'blend'
        main method.
        """
        pass

    def process(
        self,
        base_input: Union[np.ndarray, 'moderngl.Texture'],
        overlay_input: Union[np.ndarray, 'moderngl.Texture'],
        mix_weight: float = 1.0,
        dtype: Union[np.dtype, None] = None,
        **kwargs
    # TODO: Is this the expected type (?)
    # TODO: What about OpenGL textures (?)
    ) -> np.ndarray:
        """
        Blend the `base_input` provided with the also given
        `overlay_input`, using the `mix_weight` to obtain
        a single output as the result.

        The inputs should be received in uint8 format in
        the [0, 255] range, then processed with the specific
        processing method, and then turned back again to the
        uint8 format and [0, 255] range.
        """
        ParameterValidator.validate_mandatory_instance_of('base_input', base_input, [np.ndarray, 'moderngl.Texture'])
        ParameterValidator.validate_mandatory_instance_of('overlay_input', overlay_input, [np.ndarray, 'moderngl.Texture'])
        ParameterValidator.validate_mandatory_number_between('mix_weight', mix_weight, 0.0, 1.0)

        # TODO: We should always receive the inputs as
        # uint8 in [0, 255] range

        # TODO: We have to make sure the sizes are the
        # same, or force them or do something...
        _validate_inputs_and_mix_weights(
            inputs = [base_input, overlay_input],
            mix_weights = [mix_weight]
        )

        # TODO: Should we keep this functionality (?)
        # Transform to numpy arrays if textures received
        # base_input = (
        #     texture_to_frame(base_input, do_include_alpha = True)
        #     if PythonValidator.is_instance_of(base_input, 'moderngl.Texture') else
        #     base_input
        # )

        # overlay_input = (
        #     texture_to_frame(overlay_input, do_include_alpha = True)
        #     if PythonValidator.is_instance_of(overlay_input, 'moderngl.Texture') else
        #     overlay_input
        # )

        dtype = (
            base_input.dtype
            if dtype is None else
            dtype
        )

        # TODO: Size of 'base_input' and 'overlay_input' must
        # be the same, and the 'base_input' should be the size
        if mix_weight == 0:
            # We want to affect 0% to the base, so we return the
            # base directly instead of calculating, but... Y_Y
            return base_input

        # 1. Blend with the specific internal process
        blended = self._blend(
            base_input = base_input,
            overlay_input = overlay_input,
            **kwargs
        )

        # 2. Apply mix_weight to determine the percentage to affect
        blended = (
            base_input * (1 - mix_weight) + blended * mix_weight
            if mix_weight < 1.0 else
            blended
        )

        # Always turn back to uint8 in [0, 255] range
        blended = _ensure_uint8(blended)

        return blended.astype(dtype)

    def process_multiple_inputs(
        self,
        inputs: list[Union[np.ndarray, 'moderngl.Texture']],
        mix_weights: Union[list[float], float] = 1.0,
        dtype: Union[np.dtype, None] = None,
        **kwargs
    ) -> np.ndarray:
        """
        Blend all the `inputs` provided, one after another,
        applying the `mix_weight` provided, and forcing the
        result to the `dtype` if provided.

        The `mix_weight` can be a single float value, that 
        will be used for all the mixings, or a list of as
        many float values as `inputs` received, to be 
        applied individually to each mixing.
        """
        _validate_inputs_and_mix_weights(
            inputs = inputs,
            mix_weights = mix_weights
        )
        
        # We process all the 'inputs' as 'base' and 'overlay'
        # and accumulate the result
        dtype = (
            inputs[0].dtype
            if dtype is None else
            dtype
        )

        # Use the first one as the base
        base = inputs[0]

        # TODO: How do we handle the additional parameters that
        # could be an array? Maybe if it is an array, check that
        # the number of elements is the same as the number of
        # inputs, and if a single value just use it...

        for i in range(1, len(inputs)):
            overlay = inputs[i]
            mix_weight = mix_weights[i]

            # TODO: If we make a lot of different operations and
            # force the [0, 255] range in each of them, we could
            # have an accumulated error... Think if we need to
            # refactor this
            base = self.process(
                base_input = base,
                overlay_input = overlay,
                mix_weight = mix_weight
            )

        # Result is always forced to uint8 and [0, 255] when
        # processed by pairs, so we don't need  to do it
        # TODO: Maybe we can avoid 'dtype' parameter as it
        # is not useful at all...
        return base.astype(dtype)
    
"""
Specific implementations start below this class.
"""
    
# Specific implementations below
class MixBlenderCPU(_BlenderCPU):
    """
    Blend the second input with the first one
    applying the float factor (between 0.0 and
    1.0) that is passed as parameter.
    """

    def _blend(
        self,
        base_input: np.ndarray,
        overlay_input: np.ndarray,
        mix_weight: float = 1.0
    ) -> np.ndarray:
        """
        *For internal use only*

        The internal process to blend and mix the provided
        `base_input` and `overlay_input`.

        This method should not force uint8 nor [0, 255]
        range by itself as it would be done in the 'blend'
        main method.
        """
        # We do nothing because the mix is done in the
        # general 'process' method that calls this one
        return overlay_input
    
class AlphaBlenderCPU(_BlenderCPU):
    """
    Blend the different inputs by applying the
    normal and most famous alpha blending and the
    most typical used in video editing.

    This blender will use the alpha channel of the 
    overlay input, multiplied by the `blend_strength`
    parameter provided, to use it as the mixer factor
    between the base and the overlay inputs.
    """

    def _blend(
        self,
        base_input: np.ndarray,
        overlay_input: np.ndarray,
        blend_strength: float = 1.0
    ) -> np.ndarray:
        """
        *For internal use only*

        The internal process to blend and mix the provided
        `base_input` and `overlay_input`.

        (!) This method should not force uint8 nor [0, 255]
        range by itself as it would be done in the 'blend'
        main method.
        """
        # We force to have float precission for the calculations
        base_input = TextureUtils.numpy_to_float32(base_input)
        overlay_input = TextureUtils.numpy_to_float32(overlay_input)

        base_rgb, base_a = base_input[..., :3], base_input[..., 3:4]
        overlay_rgb, overlay_a = overlay_input[..., :3], overlay_input[..., 3:4]

        # Compound alpha
        alpha = overlay_a * blend_strength

        # Equivalent to mix(base, overlay, alpha) in glsl
        out_rgb = base_rgb * (1.0 - alpha) + overlay_rgb * alpha
        out_a = base_a * (1.0 - alpha) + overlay_a * alpha

        return TextureUtils.numpy_to_uint8(np.concatenate(
            [out_rgb, out_a],
            axis = -1
        ))
    
    def process(
        self,
        base_input: Union[np.ndarray, 'moderngl.Texture'],
        overlay_input: Union[np.ndarray, 'moderngl.Texture'],
        mix_weight: float = 1.0,
        dtype: Union[np.dtype, None] = None,
        blend_strength: float = 0.5
    # TODO: Is this the expected type (?)
    # TODO: What about OpenGL textures (?)
    ) -> np.ndarray:
        return super().process(
            base_input = base_input,
            overlay_input = overlay_input,
            mix_weight = mix_weight,
            dtype = dtype,
            blend_strength = blend_strength
        )
    
class AddBlenderCPU(_BlenderCPU):
    """
    Blend the different inputs by applying the
    normal and most famous alpha blending and the
    most typical used in video editing.

    This blender will increase the brightness by
    combining the colors of the base and the overlay
    inputs, using the overlay as much as the 
    `stregth` parameter is indicating.
    """

    def _blend(
        self,
        base_input: np.ndarray,
        overlay_input: np.ndarray,
        strength: float = 1.0
    ) -> np.ndarray:
        """
        *For internal use only*

        The internal process to blend and mix the provided
        `base_input` and `overlay_input`.

        This method should not force uint8 nor [0, 255]
        range by itself as it would be done in the 'blend'
        main method.
        """
        # We force to have float precission for the calculations
        base_input = TextureUtils.numpy_to_float32(base_input)
        overlay_input = TextureUtils.numpy_to_float32(overlay_input)

        # Add blending (base + overlay * strength)
        result = base_input + overlay_input * strength

        return TextureUtils.numpy_to_uint8(np.clip(result, 0.0, 1.0))
    
    def process(
        self,
        base_input: Union[np.ndarray, 'moderngl.Texture'],
        overlay_input: Union[np.ndarray, 'moderngl.Texture'],
        mix_weight: float = 1.0,
        dtype: Union[np.dtype, None] = None,
        strength: float = 1.0
    # TODO: Is this the expected type (?)
    # TODO: What about OpenGL textures (?)
    ) -> np.ndarray:
        return super().process(
            base_input = base_input,
            overlay_input = overlay_input,
            mix_weight = mix_weight,
            dtype = dtype,
            strength = strength
        )