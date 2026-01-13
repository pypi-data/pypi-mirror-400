"""
Module for the effects and nodes that are made by
putting different nodes together.
"""
from abc import abstractmethod
from typing import Union

import moderngl


class _NodeComplexGPU:
    """
    A node that is made by applying different nodes. It
    is different than the other nodes because it needs
    to import different nodes to process the input(s).

    TODO: This is, by now, just a class to identify these
    new type of nodes.
    """

    def __init__(
        self,
        opengl_context: Union['moderngl.Context', None],
        output_size: Union[tuple[int, int], None],
        **kwargs
    ):
        self._opengl_context: Union['moderngl.Context', None] = opengl_context
        self._output_size: Union[tuple[int, int], None] = output_size
        self.kwargs = kwargs

    @abstractmethod
    def process(
        self,
        # If None it must be an empty alpha texture
        base_input: Union[moderngl.Texture, 'np.ndarray', None],
        output_size: Union[tuple[int, int], None],
        **kwargs
    ) -> moderngl.Texture:
        pass


"""
Specific implementations start below this class.
"""

# TODO: This is special as it is not a node itself
class DisplayOverAtNodeComplexGPU(_NodeComplexGPU):
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

    This complex node is using the next other nodes:
    - `DisplacementWithRotationNodeCompositorGPU`
    - `AlphaBlenderGPU`

    TODO: This has no inheritance, is special and we need
    to be able to identify it as a valid one.
    """

    def __init__(
        self,
        opengl_context: Union[moderngl.Context, None],
        output_size: tuple[int, int],
        **kwargs
    ):
        super().__init__(
            opengl_context = opengl_context,
            output_size = output_size,
            **kwargs
        )

    def process(
        self,
        base_input: Union['moderngl.Texture', 'np.ndarray', None],
        overlay_input: Union['moderngl.Texture', 'np.ndarray'],
        position: tuple[int, int] = (1920 / 2, 1080 / 2),
        size: tuple[int, int] = (1920 / 2, 1080 / 2),
        rotation: int = 0
    ):
        """
        By default, the texture overlayed will be displayed in
        the center of the scene, with half of the scene size
        and no rotation.
        """
        from yta_editor_nodes_gpu.compositor import DisplacementWithRotationNodeCompositorGPU
        from yta_editor_nodes_gpu.blender import AlphaBlenderGPU

        displacement_node_processor = DisplacementWithRotationNodeCompositorGPU(
            opengl_context = self._opengl_context,
            output_size = self._output_size
        )

        output = displacement_node_processor.process(
            #base_input = background_as_numpy,
            base_input = None,
            #overlay_input = background_as_numpy,
            overlay_input = overlay_input,
            output_size = None,
            position = position,
            size = size,
            rotation = rotation
            #rotation = 0.785398 # 0.785398 = 45deg
        )

        if base_input is not None:
            #  TODO: Add just as an overlay
            blender = AlphaBlenderGPU(
                opengl_context = self._opengl_context,
                output_size = self._output_size
            )
            
            output = blender.process(
                # We don't need to care about the size because OpenGL
                # handles it
                base_input = base_input,
                overlay_input = output,
                mix_weight = 1.0,
                blend_strength = 1.0
            )

        return output