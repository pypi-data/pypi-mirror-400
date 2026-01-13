"""
This entire module is working with OpenGL.

We don't name it 'blend' instead of 'process' because
the GPU classes have the 'process' name due to the
inheritance from OpenGL classes, and we want to avoid
misunderstandings.

(!) IMPORTANT:
In all our blenders we need to include a platform
called `mix_weight` to determine the percentage of 
effect we want to apply to the output result:
- `uniform float mix_weight;  // 0.0 → only base, 1.0 → only overlay`
- `output_color = mix(base_color, overlay_color, mix_weight);`
"""
from yta_video_opengl.abstract import _OpenGLBase
from yta_editor_nodes_gpu.blender.utils import _validate_inputs_and_mix_weights
from yta_video_opengl.texture.utils import TextureUtils
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from typing import Union

import numpy as np
import moderngl


# TODO: I think this one should inherit from
# '_NodeProcessorGPU'
class _BlenderGPU(_OpenGLBase):
    """
    *Singleton class*
    
    *For internal use only*

    *This class has to be inherited*

    Class to represent a blender that uses GPU to
    blend the inputs. Base class for an OpenGL
    blender, that will be inherited by the specific
    implementations.

    The basic class of a blender to blend frames as
    opengl textures. This blender will process the
    inputs as textures and will generate also a
    texture as the output.

    Blender results can be chained and the result
    from one node can be applied on another node.

    This blender is able to work acting as an
    opacity blender, but will be used as the base
    of the classes that we will implement actually.

    The `opacity` value must be set as an uniform
    each time we are processing the 2 textures.
    """

    @property
    def fragment_shader(
        self
    ) -> str:
        """
        The code of the fragment shader.
        """
        return (
            '''
            #version 330
            uniform sampler2D base_texture;
            uniform sampler2D overlay_texture;
            uniform float mix_weight;  // 0.0 → only base, 1.0 → only overlay
            in vec2 v_uv;
            out vec4 output_color;

            void main() {
                vec4 base_color = texture(base_texture, v_uv);
                vec4 overlay_color = texture(overlay_texture, v_uv);

                // Apply global mix intensity
                output_color = mix(base_color, overlay_color, mix_weight);
            }
            '''
        )
    
    def __init__(
        self,
        opengl_context: Union[moderngl.Context, None],
        output_size: tuple[int, int],
        mix_weight: float = 1.0,
        **kwargs
    ):
        ParameterValidator.validate_mandatory_number_between('mix_weight', mix_weight, 0.0, 1.0)

        super().__init__(
            opengl_context = opengl_context,
            output_size = output_size,
            mix_weight = mix_weight,
            **kwargs
        )
    
    # TODO: Overwrite this method
    def _prepare_input_textures(
        self
    ) -> '_BlenderGPU':
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
    
    # TODO: Overwrite this method
    def process(
        self,
        base_input: Union[moderngl.Texture, np.ndarray],
        overlay_input: Union[moderngl.Texture, np.ndarray],
        output_size: Union[tuple[int, int], None] = None,
        mix_weight: float = 1.0,
        **kwargs
    ) -> moderngl.Texture:
        """
        Validate the parameters, set the textures map, process
        the mix by applying the blender logic, and return the
        result but only applied as much as the `mix_weight` 
        parameter is indicating.

        Apply the shader to the given 'base_input'
        and 'overlay_input', that must be frames or
        textures, and return the new resulting
        texture.

        You can provide any additional parameter
        in the **kwargs, but be careful because
        this could overwrite other uniforms that
        were previously set.

        We use and return textures to maintain
        the process in GPU and optimize it.
        """
        ParameterValidator.validate_mandatory_instance_of('base_input', base_input, [moderngl.Texture, np.ndarray])
        ParameterValidator.validate_mandatory_instance_of('overlay_input', overlay_input, [moderngl.Texture, np.ndarray])
        ParameterValidator.validate_mandatory_number_between('mix_weight', mix_weight, 0.0, 1.0)

        if mix_weight == 0.0:
            # If the mix_weight is 0.0 we don't want to affect
            # the base so we don't even need to process the
            # mix but return the original base input as a
            # Texture
            return (
                base_input
                if PythonValidator.is_instance_of(base_input, moderngl.Texture) else
                TextureUtils.numpy_to_texture(
                    input = base_input,
                    opengl_context = self.context
                )
            )

        textures_map = {
            'base_texture': base_input,
            'overlay_texture': overlay_input
        }

        return self._process_common(
            textures_map = textures_map,
            output_size = output_size,
            mix_weight = mix_weight,
            **kwargs
        )
    
    # TODO: This method can change according to the way
    # we need to process the inputs, that could be
    # different than by pairs
    def process_multiple_inputs(
        self,
        inputs: list[Union[np.ndarray, moderngl.Texture]],
        mix_weights: Union[list[float], float] = 1.0,
        output_size: Union[tuple[int, int], None] = None,
    ) -> moderngl.Texture:
        """
        Blend all the `inputs` provided, one after another,
        applying the `mix_weights` provided, and forcing the
        result to the `dtype` if provided.

        The `mix_weights` can be a single float value, that 
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

        # Use the first one as the base
        output = inputs[0]

        # TODO: How do we handle the additional parameters that
        # could be an array? Maybe if it is an array, check that
        # the number of elements is the same as the number of
        # inputs, and if a single value just use it...

        for i in range(1, len(inputs)):
            overlay_input = inputs[i]
            mix_weight = mix_weights[i]

            output = self.process(
                base_input = output,
                overlay_input = overlay_input,
                output_size = output_size,
                mix_weight = mix_weight,
            )

        return output
    
"""
Specific implementations start below this class.
"""
    
class MixBlenderGPU(_BlenderGPU):
    """
    Blender to blend 2 textures by using a mix float
    parameter that determines the amount of the result
    we want to mix with the input.
    """
    # It is implemented. It uses the shaders that are
    # set in the base class, so we don't need anything
    # else. I prefer it like this to keep clear which
    # class is the base class. You can use it :)
    pass

class AlphaBlenderGPU(_BlenderGPU):
    """
    Blender to blend 2 textures by using the most common
    blending method, which is the alpha.

    This blender will use the alpha channel of the 
    overlay input, multiplied by the `blend_strength`
    parameter provided, to use it as the mixer factor
    between the base and the overlay inputs.
    """

    @property
    def fragment_shader(
        self
    ) -> str:
        """
        The code of the fragment shader.
        """
        # TODO: What if no 'overlay_color.a' (?)
        return (
            '''
            #version 330
            uniform sampler2D base_texture;
            uniform sampler2D overlay_texture;
            uniform float mix_weight;  // 0.0 → only base, 1.0 → only overlay
            uniform float blend_strength;
            in vec2 v_uv;
            out vec4 output_color;

            void main() {
                vec4 base_color = texture(base_texture, v_uv);
                vec4 overlay_color = texture(overlay_texture, v_uv);

                // Use alpha channel of overlay if available
                float alpha = overlay_color.a * blend_strength;

                // Classic blending
                output_color = mix(base_color, overlay_color, alpha);

                // Apply global mix intensity
                output_color = mix(base_color, output_color, mix_weight);
            }
            '''
        )
    
    def __init__(
        self,
        opengl_context: Union[moderngl.Context, None],
        output_size: tuple[int, int]
    ):
        super().__init__(
            opengl_context = opengl_context,
            output_size = output_size
        )

    def process(
        self,
        base_input: Union[moderngl.Texture, np.ndarray],
        overlay_input: Union[moderngl.Texture, np.ndarray],
        output_size: Union[tuple[int, int], None] = None,
        mix_weight: float = 1.0,
        blend_strength: float = 0.5
    ) -> moderngl.Texture:
        """
        Validate the parameters, set the textures map, process
        the mix by applying the blender logic, and return the
        result but only applied as much as the `mix_weight` 
        parameter is indicating.

        Apply the shader to the given 'base_input'
        and 'overlay_input', that must be frames or
        textures, and return the new resulting
        texture.

        You can provide any additional parameter
        in the **kwargs, but be careful because
        this could overwrite other uniforms that
        were previously set.

        We use and return textures to maintain
        the process in GPU and optimize it.
        """
        ParameterValidator.validate_mandatory_instance_of('base_input', base_input, [moderngl.Texture, np.ndarray])
        ParameterValidator.validate_mandatory_instance_of('overlay_input', overlay_input, [moderngl.Texture, np.ndarray])
        ParameterValidator.validate_mandatory_number_between('mix_weight', mix_weight, 0.0, 1.0)
        ParameterValidator.validate_mandatory_number_between('blend_strength', blend_strength, 0.0, 1.0)

        if mix_weight == 0.0:
            # If the mix_weight is 0.0 we don't want to affect
            # the base so we don't even need to process the
            # mix but return the original base input as a
            # Texture
            return (
                base_input
                if PythonValidator.is_instance_of(base_input, moderngl.Texture) else
                TextureUtils.numpy_to_texture(
                    input = base_input,
                    opengl_context = self.context
                )
            )

        textures_map = {
            'base_texture': base_input,
            'overlay_texture': overlay_input
        }

        return self._process_common(
            textures_map = textures_map,
            output_size = output_size,
            mix_weight = mix_weight,
            blend_strength = blend_strength
        )

class AddBlenderGPU(_BlenderGPU):
    """
    Blender to blend 2 textures by adding their values.

    This blender will increase the brightness by
    combining the colors of the base and the overlay
    inputs, using the overlay as much as the 
    `stregth` parameter is indicating.
    """

    @property
    def fragment_shader(
        self
    ) -> str:
        """
        The code of the fragment shader.
        """
        return (
            '''
            #version 330
            uniform sampler2D base_texture;
            uniform sampler2D overlay_texture;
            uniform float mix_weight;  // 0.0 → only base, 1.0 → only overlay
            uniform float strength;  // 1.0 = full additive, 0.5 = subtle
            in vec2 v_uv;
            out vec4 output_color;

            void main() {
                vec4 base_color = texture(base_texture, v_uv);
                vec4 overlay_color = texture(overlay_texture, v_uv);

                vec4 result = base_color + overlay_color * strength;

                // Clamp to avoid overflow (values > 1.0)
                output_color = clamp(result, 0.0, 1.0);

                // Apply global mix intensity
                output_color = mix(base_color, output_color, mix_weight);
            }
            '''
        )
    
    def __init__(
        self,
        opengl_context: Union[moderngl.Context, None],
        output_size: tuple[int, int],
    ):
        super().__init__(
            opengl_context = opengl_context,
            output_size = output_size,
        )

    def process(
        self,
        base_input: Union[moderngl.Texture, np.ndarray],
        overlay_input: Union[moderngl.Texture, np.ndarray],
        output_size: Union[tuple[int, int], None] = None,
        mix_weight: float = 1.0,
        strength: float = 0.5
    ) -> moderngl.Texture:
        """
        Validate the parameters, set the textures map, process
        the mix by applying the blender logic, and return the
        result but only applied as much as the `mix_weight` 
        parameter is indicating.

        Apply the shader to the given 'base_input'
        and 'overlay_input', that must be frames or
        textures, and return the new resulting
        texture.

        You can provide any additional parameter
        in the **kwargs, but be careful because
        this could overwrite other uniforms that
        were previously set.

        We use and return textures to maintain
        the process in GPU and optimize it.
        """
        ParameterValidator.validate_mandatory_instance_of('base_input', base_input, [moderngl.Texture, np.ndarray])
        ParameterValidator.validate_mandatory_instance_of('overlay_input', overlay_input, [moderngl.Texture, np.ndarray])
        ParameterValidator.validate_mandatory_number_between('mix_weight', mix_weight, 0.0, 1.0)
        ParameterValidator.validate_mandatory_number_between('strength', strength, 0.0, 1.0)

        if mix_weight == 0.0:
            # If the mix_weight is 0.0 we don't want to affect
            # the base so we don't even need to process the
            # mix but return the original base input as a
            # Texture
            return (
                base_input
                if PythonValidator.is_instance_of(base_input, moderngl.Texture) else
                TextureUtils.numpy_to_texture(
                    input = base_input,
                    opengl_context = self.context
                )
            )

        textures_map = {
            'base_texture': base_input,
            'overlay_texture': overlay_input
        }

        return self._process_common(
            textures_map = textures_map,
            output_size = output_size,
            mix_weight = mix_weight,
            strength = strength
        )

# TODO: Create more
