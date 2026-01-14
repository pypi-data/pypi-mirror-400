from yta_programming.singleton import SingletonABCMeta
from abc import abstractmethod

import numpy as np



class _NodeCompositorCPU(metaclass = SingletonABCMeta):
    """
    *Singleton class*

    *For internal use only*
    
    Class to represent a node compositor that uses CPU
    to position the input in a specific place.

    This is the equivalent to `_NodeCompositorGPU` of 
    `yta-editor-nodes-gpu`, but in CPU.

    Nodes can be chained and the result from one node
    can be applied on another node.

    This _NodeCompositor is to be able to make a composition
    with different inputs. For example, placing a specific
    input in a position, with a rotation, over another input
    that acts as the base.
    """

    # TODO: Just code and the same attributes that the
    # GPU version also has
    @abstractmethod
    def process(
        self,
        # TODO: What about the type (?)
        base_input: np.ndarray,
        overlay_input: np.ndarray,
        **kwargs
    # TODO: What about the output type (?)
    ) -> np.ndarray:
        """
        Place the provided `overlay_input` over the also
        given `base_input`. 
        """
        # TODO: Specific attributes can be received as
        # **kwargs to modify the specific process
        pass

"""
Specific implementations start below this class.
"""

"""
TODO: Using Pillow is very slow, so we will not
implement this by now. But here is some code that
should work once it's modified
"""
class DisplacementWithRotationNodeCompositorCPU(_NodeCompositorCPU):
    """
    TODO: This must be implemented
    """

    def process(
        self,
        base_input: np.ndarray,
        overlay_input: np.ndarray,
        **kwargs
    ) -> np.ndarray:
        raise NotImplementedError('Not implemented yet')
# TODO: This one is a bit special because you need
# more than 1 texture, and it is also the one we
# use to move the frames, so move it from here
# class DisplacementWithRotationNodeCompositorCPU(_NodeCompositorCPU):
#     """
#     The frame, but moving and rotating over other frame.
#     """

#     def process(
#         self,
#         # TODO: What about the type (?)
#         base_input: np.ndarray,
#         overlay_input: np.ndarray,
#         position: tuple[int, int],
#         size: tuple[int, int],
#         rotation: int,
#         **kwargs
#     ):
#         from yta_numpy.utils import numpy_to_pillow

#         # TODO: Maybe 'cv2' is faster (?)
#         base_im = numpy_to_pillow(
#             frame = base_input,
#             do_read_as_rgba = True
#         )
#         ovr_im = numpy_to_pillow(
#             frame = overlay_input,
#             do_read_as_rgba = True
#         )

#         base_w, base_h = base_im.size

#         pos_x, pos_y = position
#         tgt_w = int(round(size[0]))
#         tgt_h = int(round(size[1]))

#         # Avoid 0 size
#         tgt_w = max(1, tgt_w)
#         tgt_h = max(1, tgt_h)

#         from PIL import Image

#         # Resize overlay to expected size
#         overlay_resized = ovr_im.resize((tgt_w, tgt_h), resample = Image.BICUBIC)

#         # --- Rotar alrededor del centro (expand=False mantiene bbox tamaño tgt_w x tgt_h) ---
#         # Pillow rota CCW; expand=False mantiene el canvas, recortando los bordes que sobresalgan.
#         overlay_rot = overlay_resized.rotate(rotation_degrees, resample=resample, expand=False)

#         # --- Crear capa vacía del tamaño de la base y pegar overlay en su posición centrada ---
#         overlay_layer = Image.new('RGBA', (base_w, base_h), (0, 0, 0, 0))

#         top_left_x = int(round(pos_x - tgt_w / 2.0))
#         top_left_y = int(round(pos_y - tgt_h / 2.0))

#         # Pegar usando la propia alpha de overlay_rot como máscara; paste maneja recortes fuera de bordes correctamente.
#         overlay_layer.paste(overlay_rot, (top_left_x, top_left_y), overlay_rot)

#         # --- Componer: base sobre la que overlay_layer se coloca ---
#         # Usamos alpha_composite pero requiere imágenes del mismo tamaño (ya lo son)
#         result = Image.alpha_composite(base_im, overlay_layer)

#         return np.array(result, dtype=np.uint8)