from yta_video_opengl.abstract import _OpenGLBase
from yta_validation.parameter import ParameterValidator
from typing import Union

import numpy as np
import moderngl


class _NodeCompositorGPU(_OpenGLBase):
    """
    *Singleton class*

    *For internal use only*
    
    Class to represent a node processor that uses GPU
    to composite the input into the scene, by rotating,
    positioning it, etc.

    This node will process the frame as an input
    texture and will generate also a texture as the
    output.

    Nodes can be chained and the result from one node
    can be applied on another node.
    """

    @property
    def vertex_shader(
        self
    ) -> str:
        """
        The code of the vertex shader. This is, by default,
        a rectangle made by 2 triangles that will be placed
        in the specific position, with the size provided and
        with the also given rotation.
        """
        return (
            '''
            #version 330

            in vec2 in_vert;        // Quad vertices [-1.0, 1.0]
            in vec2 in_texcoord;    // UV Coordinates: (0, 0) a (1, 1)
            out vec2 v_uv;

            uniform vec2 position;  // Center of texture
            uniform vec2 size;      // Size of texture (w, h)
            uniform float rotation; // Rotation (in degrees)

            // Resolution of the viewport
            // TODO: Turn this into a uniform with default value
            const vec2 resolution = vec2(1920.0, 1080.0);

            vec2 rotate_around_center(vec2 p, float rotation) {
                float radians = radians(rotation);
                float s = sin(radians);
                float c = cos(radians);
                mat2 rot = mat2(c, -s, s, c);
                return rot * p;
            }

            void main() {
                // Local coordinates but in [-0.5, 0.5]
                vec2 local = in_vert * 0.5;

                vec2 scaled = local * size;
                vec2 rotated = rotate_around_center(scaled, rotation);
                vec2 pos_pixels = position + rotated;

                // Pixels to normalized coordinates [-1.0, 1.0]
                vec2 ndc = (pos_pixels / resolution) * 2.0 - 1.0;

                gl_Position = vec4(ndc, 0.0, 1.0);
                v_uv = in_texcoord;
            }
            '''
        )
    
    @property
    def fragment_shader(
        self
    ) -> str:
        return (
            '''
            #version 330
            in vec2 v_uv;
            out vec4 output_color;
            uniform sampler2D base_texture;
            uniform sampler2D overlay_texture;
            uniform bool do_use_transparent_base_texture;

            void main() {
                vec4 base_color;

                if (do_use_transparent_base_texture) {
                    base_color = vec4(0.0, 0.0, 0.0, 0.0);
                } else {
                    //base_color = vec4(1.0, 1.0, 1.0, 1.0);
                    base_color = texture(base_texture, v_uv);
                }

                vec4 overlay_color = texture(overlay_texture, v_uv);
                output_color = mix(base_color, overlay_color, overlay_color.a);
                //output_color = vec4(v_uv, 0.0, 1.0);
            }
            '''
        )
    
    def _prepare_input_textures(
        self
    ) -> '_OpenGLBase':
        """
        *For internal use only*

        Set the input texture variables and handlers
        we need to manage this. This method has to be
        called only once, just to set the slot for 
        the different textures we will use (and are
        registered as textures in the shader).
        """
        self.textures.add('base_texture', 0)
        self.textures.add('overlay_texture', 1)

        return self
    
    def process(
        self,
        # If None it must be an empty alpha texture
        base_input: Union[moderngl.Texture, 'np.ndarray', None],
        overlay_input: Union[moderngl.Texture, 'np.ndarray'],
        output_size: Union[tuple[int, int], None],
        #output_size: Union[tuple[int, int], None] = None,
        # TODO: We need the value as pixels in (1920, 1080)
        position: tuple[int, int],
        size: tuple[int, int],
        rotation: int,
        **kwargs
    ) -> moderngl.Texture:
        """
        Mix the `processed_input` with the 
        `original_input` as the `selecction_mask_input`
        says.

        The `position` and `size` parameters must be in
        pixels (in a scene size of `(1920, 1080)`). The
        rotation must be an `int` value representing the
        degrees.

        You can provide any additional parameter
        in the **kwargs, but be careful because
        this could overwrite other uniforms that
        were previously set.

        We use and return textures to maintain
        the process in GPU and optimize it.
        """
        ParameterValidator.validate_instance_of('base_input', base_input, [moderngl.Texture, 'ndarray'])
        ParameterValidator.validate_mandatory_instance_of('overlay_input', overlay_input, [moderngl.Texture, 'ndarray'])

        do_use_transparent_base_texture = base_input is None

        textures_map = {}

        if base_input is not None:
            # TODO: The size will be obtained from the first texture
            # dynamically, but if we don't provide the base texture,
            # it will be created as a completely transparent one,
            # that doesn't have any size in the 'textures_map' var
            textures_map['base_texture'] = base_input
        
        textures_map = textures_map | {
            # TODO: I think the 'base_input' should be forced to
            # be a completely transparent texture here
            'overlay_texture': overlay_input
        }

        return self._process_common(
            textures_map = textures_map,
            output_size = output_size,
            position = position,
            size = size,
            rotation = rotation,
            do_use_transparent_base_texture = do_use_transparent_base_texture,
            **kwargs
        )
    
"""
Specific implementations start below this class.
"""

class DisplacementWithRotationNodeCompositorGPU(_NodeCompositorGPU):
    """
    The frame, but moving and rotating over other frame.
    """

    pass