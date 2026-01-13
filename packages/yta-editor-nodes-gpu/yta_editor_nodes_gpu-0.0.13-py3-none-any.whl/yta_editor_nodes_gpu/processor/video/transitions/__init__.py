"""
TODO: This module doesn't use 't' but 'progress'
so it is not a child of 'processor.video', maybe
we should move it to be 'processor.transitions'
instead of 'processor.video.transitions'... (?)
"""
from yta_video_opengl.abstract import _OpenGLBase
from yta_validation.parameter import ParameterValidator
from typing import Union

import numpy as np
import moderngl


class _TransitionProcessorGPU(_OpenGLBase):
    """
    *Abstract class*

    *For internal use only*

    A transition between the frames of 2 videos.

    This transition is made with GPU (OpenGL).
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
            uniform sampler2D first_texture;
            uniform sampler2D second_texture;
            uniform float progress;     // 0.0 → full A, 1.0 → full B
            in vec2 v_uv;
            out vec4 output_color;

            void main() {
                // Horizontal version (right to left)
                vec2 uv_first = v_uv + vec2(-progress, 0.0);
                vec2 uv_second = v_uv + vec2(1.0 - progress, 0.0);

                vec4 color_first = texture(first_texture, uv_first);
                vec4 color_second = texture(second_texture, uv_second);

                if (uv_first.x < 0.0) {
                    output_color = color_second;
                } else if (uv_second.x > 1.0) {
                    output_color = color_first;
                } else {
                    // A and B frames are shown at the same time
                    output_color = mix(color_first, color_second, progress);
                }
            }
            '''
        )
    
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

    def _prepare_input_textures(
        self
    ) -> '_OpenGLBase':
        """
        *For internal use only*

        *This method should be overwritten*

        Set the input texture variables and handlers
        we need to manage this. This method has to be
        called only once, just to set the slot for 
        the different textures we will use (and are
        registered as textures in the shader).
        """
        self.textures.add('first_texture', 0)
        self.textures.add('second_texture', 1)

        return self
    
    def process(
        self,
        first_input: Union[moderngl.Texture, np.ndarray],
        second_input: Union[moderngl.Texture, np.ndarray],
        progress: float,
        output_size: Union[tuple[int, int], None] = None,
        **kwargs
    ) -> moderngl.Texture:
        """
        Validate the parameters, set the textures map, process
        it and return the result according to the `progress`
        provided.

        You can provide any additional parameter
        in the **kwargs, but be careful because
        this could overwrite other uniforms that
        were previously set.

        We use and return textures to maintain
        the process in GPU and optimize it.
        """
        ParameterValidator.validate_mandatory_instance_of('first_input', first_input, [moderngl.Texture, np.ndarray])
        ParameterValidator.validate_mandatory_instance_of('second_input', second_input, [moderngl.Texture, np.ndarray])
        ParameterValidator.validate_mandatory_positive_float('progress', progress, do_include_zero = True)

        textures_map = {
            'first_texture': first_input,
            'second_texture': second_input
        }

        return self._process_common(
            textures_map = textures_map,
            output_size = output_size,
            progress = progress,
            **kwargs
        )
    
"""
Specific implementations start below this class.
"""

class SlideTransitionProcessorGPU(_TransitionProcessorGPU):
    """
    A transition between the frames of 2 videos, sliding
    from right to left.

    This transition is made with GPU (OpenGL).
    """

    # TODO: I know it is the same as in the base class
    # but I want it like that
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
            uniform sampler2D first_texture;
            uniform sampler2D second_texture;
            uniform float progress;     // 0.0 → full A, 1.0 → full B
            in vec2 v_uv;
            out vec4 output_color;

            void main() {
                // Horizontal version (slide to right)
                //vec2 uv_first = v_uv + vec2(-progress, 0.0);
                //vec2 uv_second = v_uv + vec2(1.0 - progress, 0.0);

                // Horizontal version (slide to left)
                vec2 uv_first = v_uv + vec2(progress, 0.0);
                vec2 uv_second = v_uv + vec2(-1.0 + progress, 0.0);

                vec4 color_first = texture(first_texture, uv_first);
                vec4 color_second = texture(second_texture, uv_second);

                // Horizontal version (slide to right)
                //if (uv_first.x < 0.0) {
                //    output_color = color_second;
                //} else if (uv_second.x > 1.0) {
                //    output_color = color_first;
                //} else {
                //    // A and B frames are shown at the same time
                //    output_color = mix(color_first, color_second, progress);
                //}

                // Horizontal version (slide t o left)
                if (uv_first.x > 1.0) {
                    output_color = color_second;
                } else if (uv_second.x < 0.0) {
                    output_color = color_first;
                } else {
                    output_color = mix(color_first, color_second, progress);
                }
            }
            '''
        )
    
class CrossfadeTransitionProcessorGPU(_TransitionProcessorGPU):
    """
    A transition between the frames of 2 videos,
    transforming the first one into the second one.

    This transition is made with GPU (OpenGL).
    """

    @property
    def fragment_shader(
        self
    ) -> str:
        return (
            """
            #version 330
            uniform sampler2D first_texture;
            uniform sampler2D second_texture;
            uniform float progress; // 0 = full A, 1 = full B
            in vec2 v_uv;
            out vec4 output_color;
            void main() {
                vec4 color_first = texture(first_texture, v_uv);
                vec4 color_second = texture(second_texture, v_uv);
                output_color = mix(color_first, color_second, progress);
            }
            """
        )
    
class DistortedCrossfadeTransitionProcessorGPU(_TransitionProcessorGPU):
    """
    A transition between the frames of 2 videos,
    transforming the first one into the second one
    with a distortion in between.

    This transition is made with GPU (OpenGL).
    """

    @property
    def fragment_shader(
        self
    ) -> str:
        return (
            """
            #version 330
            uniform sampler2D first_texture;
            uniform sampler2D second_texture;
            uniform float progress;   // 0.0 -> A, 1.0 -> B
            uniform float intensity;  // Distortion control
            in vec2 v_uv;
            out vec4 output_color;

            const int passes = 6;

            void main() {
                vec4 c1 = vec4(0.0);
                vec4 c2 = vec4(0.0);

                float disp = intensity * (0.5 - distance(0.5, progress));
                for (int xi=0; xi<passes; xi++) {
                    float x = float(xi) / float(passes) - 0.5;
                    for (int yi=0; yi<passes; yi++) {
                        float y = float(yi) / float(passes) - 0.5;
                        vec2 v = vec2(x, y);
                        float d = disp;
                        c1 += texture(first_texture, v_uv + d * v);
                        c2 += texture(second_texture, v_uv + d * v);
                    }
                }
                c1 /= float(passes * passes);
                c2 /= float(passes * passes);
                output_color = mix(c1, c2, progress);
            }
            """
        )
    
    def __init__(
        self,
        opengl_context: Union[moderngl.Context, None],
        # TODO: Review this
        output_size: tuple[int, int] = (1920, 1080),
        intensity: float = 1.0,
        **kwargs
    ):
        super().__init__(
            opengl_context = opengl_context,
            output_size = output_size,
            intensity = intensity,
            **kwargs
        )

class AlphaPediaMaskTransitionProcessorGPU(_TransitionProcessorGPU):
    """
    A transition made by using a custom mask to
    join the 2 videos. This mask is specifically
    obtained from the AlphaPediaYT channel in which
    we upload specific masking videos.

    Both videos will be placed occupying the whole
    scene, just overlapping by using the transition
    video mask, but not moving the frame through 
    the screen like other classes do (like the
    FallingBars).
    """

    # TODO: I think I don't need a 'progress' but just
    # mix both frames as much as the alpha (or white
    # presence) tells
    @property
    def fragment_shader(
        self
    ) -> str:
        return (
            """
            #version 330

            uniform sampler2D first_texture;
            uniform sampler2D second_texture;
            uniform sampler2D mask_texture;

            uniform float progress;  // 0.0 → full A, 1.0 → full B
            uniform bool use_alpha_channel;   // True to use the alpha channel
            //uniform float contrast;  // Optional contrast to magnify the result

            in vec2 v_uv;
            out vec4 output_color;

            void main() {
                vec4 first_color = texture(first_texture, v_uv);
                vec4 second_color = texture(second_texture, v_uv);
                vec4 mask_color = texture(mask_texture, v_uv);

                // Mask alpha or red?
                float mask_value = use_alpha_channel ? mask_color.a : mask_color.r;

                // Optional contrast
                //mask_value = clamp((mask_value - 0.5) * contrast + 0.5, 0.0, 1.0);
                mask_value = clamp((mask_value - 0.5) + 0.5, 0.0, 1.0);

                float t = smoothstep(0.0, 1.0, mask_value + progress - 0.5);

                output_color = mix(first_color, second_color, t);
            }
            """
        )
    
    def _prepare_input_textures(
        self
    ) -> None:
        """
        *For internal use only*

        Set the input texture variables and handlers
        we need to manage this.
        """
        self.textures.add('first_texture', 0)
        self.textures.add('second_texture', 1)
        self.textures.add('mask_texture', 2)
    
    def process(
        self,
        first_input: Union[moderngl.Texture, 'np.ndarray'],
        second_input: Union[moderngl.Texture, 'np.ndarray'],
        mask_input: Union[moderngl.Texture, 'np.ndarray'],
        progress: float,
        output_size: Union[tuple[int, int], None] = None,
        **kwargs
    ) -> moderngl.Texture:
        """
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
        ParameterValidator.validate_mandatory_instance_of('first_input', first_input, [moderngl.Texture, np.ndarray])
        ParameterValidator.validate_mandatory_instance_of('second_input', second_input, [moderngl.Texture, np.ndarray])
        ParameterValidator.validate_mandatory_instance_of('mask_input', mask_input, [moderngl.Texture, np.ndarray])
        ParameterValidator.validate_mandatory_positive_float('progress', progress, do_include_zero = True)

        textures_map = {
            'first_texture': first_input,
            'second_texture': second_input,
            'mask_texture': mask_input
        }

        # TODO: There is an 'use_alpha_channel' uniform to use
        # the alpha instead of the red color of the frame value,
        # but the red is working for our AlphaPedia videos, so...

        kwargs = {
            **kwargs,
            'progress': progress
        }

        return self._process_common(
            textures_map = textures_map,
            output_size = output_size,
            **kwargs
        )
    
class CircleOpeningTransitionProcessorGPU(_TransitionProcessorGPU):
    """
    A transition between the frames of 2 videos in
    which the frames are mixed by generating a circle
    that grows from the middle to end fitting the 
    whole screen.

    This transition is made with GPU (OpenGL).
    """

    @property
    def fragment_shader(
        self
    ) -> str:
        return (
            """
            #version 330
            #define UNIQUE_ID_{id(self)}
            uniform sampler2D first_texture;
            uniform sampler2D second_texture;
            uniform float progress;  // 0.0 → full A, 1.0 → full B
            uniform float border_smoothness; // 0.02 is a good value

            in vec2 v_uv;
            out vec4 output_color;

            void main() {
                // Obtain the size automatically from the texture
                vec2 output_size = vec2(textureSize(first_texture, 0));

                vec2 pos = v_uv * output_size;
                vec2 center = output_size * 0.5;

                // Distance from center
                float dist = distance(pos, center);

                // Radius of current circle
                float max_radius = length(center);
                float radius = progress * max_radius;

                vec4 first_color = texture(first_texture, v_uv);
                vec4 second_color = texture(second_texture, v_uv);

                // With smooth circle
                // TODO: Make this customizable
                float mask = 1.0 - smoothstep(radius - border_smoothness * max_radius, radius + border_smoothness * max_radius, dist);
                output_color = mix(first_color, second_color, mask);
            }
            """
        )

    def __init__(
        self,
        opengl_context: Union[moderngl.Context, None],
        # TODO: Review this
        output_size: tuple[int, int] = (1920, 1080),
        border_smoothness: float = 0.02,
        **kwargs
    ):
        super().__init__(
            opengl_context = opengl_context,
            # TODO: Maybe 'output_size' has to be the texture size
            # by default
            output_size = output_size,
            border_smoothness = border_smoothness,
            **kwargs
        )
    
class CircleClosingTransitionProcessorGPU(_TransitionProcessorGPU):
    """
    A transition between the frames of 2 videos in
    which the frames are mixed by generating a circle
    that grows from the middle to end fitting the 
    whole screen.

    This transition is made with GPU (OpenGL).
    """

    @property
    def fragment_shader(
        self
    ) -> str:
        return (
            """
            #version 330

            uniform sampler2D first_texture;
            uniform sampler2D second_texture;
            uniform float progress;  // 0.0 → full A, 1.0 → full B
            uniform float border_smoothness; // 0.02 is a good value

            in vec2 v_uv;
            out vec4 output_color;

            void main() {
                // Obtain the size automatically from the texture
                vec2 output_size = vec2(textureSize(first_texture, 0));

                vec2 pos = v_uv * output_size;
                vec2 center = output_size * 0.5;

                // Distance from center
                float dist = distance(pos, center);

                // Radius of current circle
                float max_radius = length(center);
                float radius = (1.0 - progress) * max_radius;

                vec4 first_color = texture(first_texture, v_uv);
                vec4 second_color = texture(second_texture, v_uv);

                // With smooth circle
                // TODO: Make this customizable
                float mask = smoothstep(radius - border_smoothness * max_radius, radius + border_smoothness * max_radius, dist);
                output_color = mix(first_color, second_color, mask);
            }
            """
        )

    def __init__(
        self,
        opengl_context: Union[moderngl.Context, None],
        # TODO: Review this
        output_size: tuple[int, int] = (1920, 1080),
        border_smoothness: float = 0.02,
        **kwargs
    ):
        super().__init__(
            opengl_context = opengl_context,
            # TODO: Maybe 'output_size' has to be the texture size
            # by default
            output_size = output_size,
            border_smoothness = border_smoothness,
            **kwargs
        )
    
# TODO: This effect is not working according to
# the progress, you cannot use normal timing
class BarsFallingTransitionProcessorGPU(_TransitionProcessorGPU):
    """
    A transition between the frames of 2 videos in which
    a set of bars fall with the first video to let the
    second one be seen.

    Extracted from here:
    - https://gl-transitions.com/editor/DoomScreenTransition

    This transition is made with GPU (OpenGL).
    """

    @property
    def fragment_shader(
        self
    ) -> str:
        return (
            """
            #version 330

            uniform sampler2D first_texture;
            uniform sampler2D second_texture;
            uniform float progress; // 0.0 → start, 1.0 → end

            uniform int number_of_bars;           
            uniform float amplitude;        // Speed
            uniform float noise;            // Extra noise [0.0, 1.0]
            uniform float frequency;        // Wave frequency
            uniform float drip_scale;       // Falling from center

            in vec2 v_uv;
            out vec4 output_color;

            // pseudo-random from integer
            float rand(int num) {
                return fract(mod(float(num) * 67123.313, 12.0) * sin(float(num) * 10.3) * cos(float(num)));
            }

            // Wave for vertical distortion
            float wave(int num) {
                float fn = float(num) * frequency * 0.1 * float(number_of_bars);
                return cos(fn * 0.5) * cos(fn * 0.13) * sin((fn + 10.0) * 0.3) / 2.0 + 0.5;
            }

            // Vertical curve to borders
            float drip(int num) {
                return sin(float(num) / float(number_of_bars - 1) * 3.141592) * drip_scale;
            }

            // Displacement for a bar
            float pos(int num) {
                float w = wave(num);
                float r = rand(num);
                float base = (noise == 0.0) ? w : mix(w, r, noise);
                return base + ((drip_scale == 0.0) ? 0.0 : drip(num));
            }

            void main() {
                int bar = int(v_uv.x * float(number_of_bars));

                float scale = 1.0 + pos(bar) * amplitude;
                float phase = progress * scale;
                float pos_y = v_uv.y;

                vec2 p;
                vec4 color;

                if (phase + pos_y < 1.0) {
                    // Frame A is visible
                    p = vec2(v_uv.x, v_uv.y + mix(0.0, 1.0, phase));
                    color = texture(first_texture, p);
                } else {
                    // Frame B is visible
                    color = texture(second_texture, v_uv);
                }

                output_color = color;
            }
            """
        )

    def __init__(
        self,
        opengl_context: Union[moderngl.Context, None],
        # TODO: Review this
        output_size: tuple[int, int] = (1920, 1080),
        number_of_bars: int = 30,
        amplitude: float = 2.0,
        noise: float = 0.1, # [0.0, 1.0]
        frequency: float = 0.5,
        drip_scale: float = 0.5,
        **kwargs
    ):
        super().__init__(
            opengl_context = opengl_context,
            output_size = output_size,
            number_of_bars = number_of_bars,
            amplitude = amplitude,
            noise = noise,
            frequency = frequency,
            drip_scale = drip_scale,
            **kwargs
        )

    
"""
Note for the developer:

Here below you have a shader that allows you
to create more slide transitions (vertical,
diagonal) but have to be refactored because
the mixing part is not working properly
according to the position. The code was made
for an horizontal slide but has to be adapted
to the other movements.

Code here below:

#version 330

// FRAGMENT SHADER — Slide horizontal
uniform sampler2D texA;
uniform sampler2D texB;
uniform float progress;     // 0.0 → full A, 1.0 → full B

in vec2 frag_uv;
out vec4 frag_color;

void main() {
    // Horizontal version (right to left)
    vec2 uvA = frag_uv + vec2(-progress, 0.0);
    vec2 uvB = frag_uv + vec2(1.0 - progress, 0.0);
    
    // Horizontal version (left to right)
    //vec2 uvA = frag_uv + vec2(progress, 0.0);
    //vec2 uvB = frag_uv + vec2(-1.0 + progress, 0.0);

    // Vertical version (top to bottom)
    // TODO: We need to adjust the color mixin
    // to make it fit the type of transition
    //vec2 uvA = frag_uv + vec2(0.0, -progress);
    //vec2 uvB = frag_uv + vec2(0.0, 1.0 - progress);

    // Diagonal version (top left to bottom right)
    //vec2 uvA = frag_uv + vec2(-progress, -progress);
    //vec2 uvB = frag_uv + vec2(1.0 - progress, 1.0 - progress);

    vec4 colorA = texture(texA, uvA);
    vec4 colorB = texture(texB, uvB);

    if (uvA.x < 0.0) {
        frag_color = colorB;
    } else if (uvB.x > 1.0) {
        frag_color = colorA;
    } else {
        // A and B frames are shown at the same time
        frag_color = mix(colorA, colorB, progress);
    }
}
"""