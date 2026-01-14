"""
TODO: This module doesn't use 't' but 'progress'
so it is not a child of 'processor.video', maybe
we should move it to be 'processor.transitions'
instead of 'processor.video.transitions'... (?)
"""
# TODO: Should we keep this functionality (?)
# from yta_video_opengl.utils import texture_to_frame
from yta_programming.singleton import SingletonABCMeta
from yta_validation import PythonValidator
from abc import abstractmethod
from typing import Union

import numpy as np


class _TransitionProcessorCPU(metaclass = SingletonABCMeta):
    """
    *Abstract class*

    *For internal use only*

    A transition between the frames of 2 videos.

    This transition is made with CPU (numpy).
    """

    @abstractmethod
    def process(
        self,
        # TODO: What about the type (?)
        first_input: Union['moderngl.Texture', np.ndarray],
        second_input: Union['moderngl.Texture', np.ndarray],
        progress: float,
        **kwargs
    ) -> np.ndarray:
        """
        Process the `first_input` and `second_input` and
        generate the transition frame according to the
        `progress` of the transition provided.
        """
        # TODO: Specific attributes can be received as
        # **kwargs to modify the specific process
        pass

"""
Specific implementations start below this class.
"""

class SlideTransitionProcessorCPU(_TransitionProcessorCPU):
    """
    A transition in which the frames goes from one
    side to the other, disappearing the first one
    and appearing the second one.
    """

    def process(
        self,
        # TODO: What about the type (?)
        first_input: Union['moderngl.Texture', np.ndarray],
        second_input: Union['moderngl.Texture', np.ndarray],
        progress: float
    ) -> np.ndarray:
        """
        Process the `first_input` and `second_input` and
        generate the transition frame according to the
        `progress` of the transition provided.
        """
        # TODO: Should we keep this functionality (?)
        # first_input = (
        #     texture_to_frame(first_input, do_include_alpha = True)
        #     if PythonValidator.is_instance_of(first_input, 'moderngl.Texture') else
        #     first_input
        # )

        # second_input = (
        #     texture_to_frame(second_input, do_include_alpha = True)
        #     if PythonValidator.is_instance_of(second_input, 'moderngl.Texture') else
        #     second_input
        # )

        # TODO: What do we do in this case (?)
        assert first_input.shape == second_input.shape, "Los frames deben tener la misma forma"

        h, w, c = first_input.shape
        frame_out = np.zeros_like(first_input)

        # By default we are only handling 'left' direction
        direction = 'left'

        offset_x = 0
        # offset_y = 0
        if direction == 'left':
            offset_x = int(w * progress)
            if offset_x < w:
                frame_out[:, :w - offset_x] = first_input[:, offset_x:]
            if offset_x > 0:
                frame_out[:, w - offset_x:] = second_input[:, :offset_x]

        # elif direction == 'right':
        #     offset_x = int(w * progress)
        #     if offset_x < w:
        #         frame_out[:, offset_x:] = first_input[:, :w - offset_x]
        #     if offset_x > 0:
        #         frame_out[:, :offset_x] = second_input[:, w - offset_x:]

        # elif direction == 'up':
        #     offset_y = int(h * progress)
        #     if offset_y < h:
        #         frame_out[:h - offset_y, :] = first_input[offset_y:, :]
        #     if offset_y > 0:
        #         frame_out[h - offset_y:, :] = second_input[:offset_y, :]

        # elif direction == 'down':
        #     offset_y = int(h * progress)
        #     if offset_y < h:
        #         frame_out[offset_y:, :] = first_input[:h - offset_y, :]
        #     if offset_y > 0:
        #         frame_out[:offset_y, :] = second_input[h - offset_y:, :]

        return frame_out