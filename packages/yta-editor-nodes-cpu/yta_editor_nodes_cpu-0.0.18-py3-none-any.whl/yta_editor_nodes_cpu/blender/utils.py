"""
TODO: This module is duplicated as it is repeated
in the 'yta-editor-nodes-gpu' library. It should
be in a 'yta-editor-nodes-common' library.
"""
from yta_validation.parameter import ParameterValidator
from yta_validation.number import NumberValidator
from yta_validation import PythonValidator
from typing import Union

import numpy as np


def _validate_inputs_and_mix_weights(
    inputs: list[Union[np.ndarray, 'moderngl.Texture']],
    mix_weights: Union[list[float], float] = 1.0,
) -> None:
    """
    *For internal use only*
    
    Validate the provided 'inputs' and 'mix_weights' raising
    an exception if something wrong was found.
    """
    ParameterValidator.validate_mandatory_list_of_these_instances('inputs', inputs, [np.ndarray, 'moderngl.Texture'])

    if len(inputs) < 2:
        raise Exception('The amount of "inputs" provided is less than 2.')
    
    if not all(input.size == inputs[0].size for input in inputs):
        # TODO: Should we raise this exception (?)
        raise Exception('All the inputs do not have the same size.')

    # Validate 'mix_weights' as a single or list of floats
    # in the [0.0, 1.0] range
    if PythonValidator.is_list_of_float(mix_weights):
        if len(mix_weights) != (len(inputs) - 1):
            raise Exception('The number of "mix_weights" values provided is not the same as "inputs".')
        
        for mix_weight in mix_weights:
            ParameterValidator.validate_mandatory_number_between('mix_weight', mix_weight, 0.0, 1.0)
    elif NumberValidator.is_number_between(mix_weights, 0.0, 1.0):
        mix_weights = [mix_weights] * len(inputs)
    else:
        raise Exception('The "mix_weights" parameter provided is not valid.')
    
    
def _clip_ndarray(
    input: np.ndarray,
    min: int = 0,
    max: int = 255
) -> np.ndarray:
    """
    *For internal use only*

    Clip the provided `input` numpy array with the also
    given `min` and `max` limits.
    """
    return np.clip(
        a = input,
        a_min = min,
        a_max = max
    )

def _get_stacked(
    inputs: list[np.ndarray]
) -> np.ndarray:
    """
    *For internal use only*

    Get the `inputs` but stacked.
    """
    return np.stack(
        arrays = inputs,
        axis = 0
    )

def _ensure_uint8(
    array: np.ndarray
) -> np.ndarray:
    """
    Ensure that the 'array' numpy array provided is in
    the uint8 [0, 255] range.

    This method will clip the array once it's been
    transformed (if necessary) and forced to be uint8.
    """
    if array.dtype == np.uint8:
        return array

    array = array.astype(np.float32)

    array = (
        array * 255.0
        # Detect normalized [0.0, 1.0] or in [0, 255]
        if array.max() <= 1.0 else
        array
    )

    return _clip_ndarray(array).astype(np.uint8)