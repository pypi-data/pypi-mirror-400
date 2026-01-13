from yta_editor_nodes_gpu.processor import _NodeProcessorGPU
from typing import Union

import moderngl


class _VideoNodeProcessorGPU(_NodeProcessorGPU):
    """
    *Abstract class*

    *Singleton class*

    *For internal use only*

    Class to represent a node processor that uses GPU
    to transform the input but it is meant to video
    processing, so it implements a 'time' parameter to
    manipulate the frames according to that time
    moment.

    This class must be implemented by any processor
    that uses GPU to modify an input.
    """

    def __init__(
        self,
        opengl_context: Union[moderngl.Context, None],
        output_size: tuple[int, int],
        **kwargs
    ):
        """
        Provide all the variables you want to be initialized
        as uniforms at the begining for the global OpenGL
        animation in the `**kwargs`.

        The `output_size` is the size (width, height) of the
        texture that will be obtained as result. This size
        can be modified when processing a specific input, but
        be consider the cost of resources of modifying the 
        size, that will regenerate the output texture.
        """
        super().__init__(
            opengl_context = opengl_context,
            output_size = output_size,
            **kwargs
        )

    def __reinit__(
        self,
        opengl_context: Union[moderngl.Context, None] = None,
        output_size: Union[tuple[int, int], None] = None,
        **kwargs
    ):
        super().__reinit__(
            opengl_context = opengl_context,
            output_size = output_size,
            **kwargs
        )
    
    def process(
        self,
        input: Union[moderngl.Texture, 'np.ndarray'],
        # TODO: What about this output size (?)
        output_size: Union[tuple[int, int], None] = None,
        t: float = 0.0,
        **kwargs
    # TODO: What about the output type (?)
    ) -> moderngl.Texture:
        """
        Process the provided `input` and transform it by
        using the code that is defined here according to
        the `t` time moment provided.

        Apply the shader to the 'input', that
        must be a frame or a texture, and return
        the new resulting texture.

        You can provide any additional parameter
        in the **kwargs, but be careful because
        this could overwrite other uniforms that
        were previously set.

        We use and return textures to maintain
        the process in GPU and optimize it.
        """
        return super().process(
            input = input,
            output_size = output_size,
            time = t,
            **kwargs
        )
    
"""
Specific implementations start below this class.
"""

class BreathingFrameVideoNodeProcessorGPU(_VideoNodeProcessorGPU):
    """
    The frame but as if it was breathing.
    """

    @property
    def fragment_shader(
        self
    ) -> str:
        return (
            '''
            #version 330
            uniform sampler2D base_texture;
            uniform float time;
            uniform float zoom;
            in vec2 v_uv;
            out vec4 output_color;
            // Use uniforms to be customizable

            void main() {
                // Dynamic zoom scaled with t
                float scale = 1.0 + zoom * sin(time * 2.0);
                vec2 center = vec2(0.5, 0.5);

                // Recalculate coords according to center
                vec2 uv = (v_uv - center) / scale + center;

                // Clamp to avoid artifacts
                uv = clamp(uv, 0.0, 1.0);

                output_color = texture(base_texture, uv);
            }
            '''
        )

    def __init__(
        self,
        opengl_context: Union[moderngl.Context, None],
        output_size: tuple[int, int],
        zoom: float = 0.05
        # TODO: Handle dynamic parameters with None
    ):
        """
        Provide all the variables you want to be initialized
        as uniforms at the begining for the global OpenGL
        animation in the `**kwargs`.

        The `output_size` is the size (width, height) of the
        texture that will be obtained as result. This size
        can be modified when processing a specific input, but
        be consider the cost of resources of modifying the 
        size, that will regenerate the output texture.
        """
        super().__init__(
            opengl_context = opengl_context,
            output_size = output_size,
            # Uniforms
            zoom = zoom
        )

    def __reinit__(
        self,
        opengl_context: Union[moderngl.Context, None] = None,
        output_size: Union[tuple[int, int], None] = None,
        zoom: Union[float, None] = None
        # TODO: Handle dynamic parameters with None
    ):
        super().__reinit__(
            opengl_context = opengl_context,
            output_size = output_size,
            zoom = zoom
        )
    
class WavingFramesVideoNodeProcessorGPU(_VideoNodeProcessorGPU):
    """
    The GPU processor of the video frames that are
    transformed into a wave.

    TODO: Explain this better.
    """

    @property
    def fragment_shader(
        self
    ) -> str:
        return (
            '''
            #version 330
            uniform sampler2D base_texture;
            uniform float time;
            uniform float amplitude;
            uniform float frequency;
            uniform float speed;
            uniform bool do_use_transparent_pixels;
            in vec2 v_uv;
            out vec4 output_color;

            void main() {
                float wave = sin(v_uv.x * frequency + time * speed) * amplitude;
                vec2 uv = vec2(v_uv.x, v_uv.y + wave);

                // Si el UV se sale del rango, devolvemos transparencia
                if ((uv.y < 0.0 || uv.y > 1.0) && do_use_transparent_pixels) {
                    output_color = vec4(0.0, 0.0, 0.0, 0.0);
                } else {
                    output_color = texture(base_texture, uv);
                }
            }
            '''
        )
    
    # TODO: This below doesn't use transparent pixels but
    # the other pixels of the image instead
    """
    void main() {
        float wave = sin(v_uv.x * frequency + time * speed) * amplitude;
        vec2 uv = vec2(v_uv.x, v_uv.y + wave);
        output_color = texture(base_texture, uv);
    }
    """
    
    def __init__(
        self,
        opengl_context: Union[moderngl.Context, None],
        output_size: tuple[int, int],
        # Uniforms
        amplitude: float = 0.05,
        frequency: float = 10.0,
        speed: float = 2.0,
        do_use_transparent_pixels: bool = False
    ):
        super().__init__(
            opengl_context = opengl_context,
            output_size = output_size,
            # Uniforms
            amplitude = amplitude,
            frequency = frequency,
            speed = speed,
            do_use_transparent_pixels = do_use_transparent_pixels
        )

    def __reinit__(
        self,
        opengl_context: Union[moderngl.Context, None] = None,
        output_size: Union[tuple[int, int], None] = None,
        # Uniforms
        amplitude: Union[float, None] = None,
        frequency: Union[float, None] = None,
        speed: Union[float, None] = None,
        do_use_transparent_pixels: Union[bool, None] = None
    ):
        super().__reinit__(
            opengl_context = opengl_context,
            output_size = output_size,
            amplitude = amplitude,
            frequency = frequency,
            speed = speed,
            do_use_transparent_pixels = do_use_transparent_pixels
        )
