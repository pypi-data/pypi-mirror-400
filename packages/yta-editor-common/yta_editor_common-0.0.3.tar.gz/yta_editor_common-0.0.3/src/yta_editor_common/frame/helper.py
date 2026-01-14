from yta_programming.decorators.requires_dependency import requires_dependency
from typing import Union


class FrameHelper:
    """
    Class to simplify the way we handle frames from
    their different sources and according to the
    different and possible types.

    Possible frame types:
    - `av.VideoFrame`
    - `np.ndarray`
    - `moderngl.Texture`
    """

    @staticmethod
    @requires_dependency('moderngl', 'yta_editor_utils', 'moderngl')
    @requires_dependency('numpy', 'yta_editor_utils', 'numpy')
    def ndarray_to_texture(
        frame: 'np.ndarray',
        moderngl_context: Union['moderngl.Context', None],
        do_include_alpha: bool = True
    ) -> 'moderngl.Texture':
        """
        *Optional dependency `moderngl` (imported as `moderngl`) required*

        Transform the `numpy.ndarray` `frame` provided into a
        `moderngl.Texture` frame.
        """
        import moderngl

        # TODO: Crete 'moderngl_context' if None. I have a
        # class called 'OpenGLContext' to get it

        # We consider HWC format to obtain the size
        height, width = frame.shape[:2]

        return moderngl_context.texture(
            (width, height),
            # This was originally 4 only but I added the bool
            components = (
                4
                if do_include_alpha else
                3
            ),
            data = frame.tobytes()
        )
    
    @staticmethod
    @requires_dependency('av', 'yta_editor_utils', 'av')
    @requires_dependency('numpy', 'yta_editor_utils', 'numpy')
    def ndarray_to_videoframe(
        frame: 'np.ndarray',
        do_include_alpha: bool = True,
        pts: Union[int, None] = None,
        time_base: Union['Fraction', None] = None
    ) -> 'av.VideoFrame':
        """
        *Optional dependency `av` (imported as `av`) required*

        Transform the `numpy.ndarray` `frame` provided into a
        `av.VideoFrame` frame.
        """
        import av

        format = (
            'rgba'
            if do_include_alpha else
            'rgb24'
        )

        frame = av.VideoFrame.from_ndarray(
            array = frame,
            format = format
        )

        if pts is not None:
            frame.pts = pts

        if time_base is not None:
            frame.time_base = time_base

        return frame

    @staticmethod
    @requires_dependency('av', 'yta_editor_utils', 'av')
    @requires_dependency('numpy', 'yta_editor_utils', 'numpy')
    def videoframe_to_ndarray(
        frame: 'av.VideoFrame',
        do_include_alpha: bool = True
    ) -> 'np.ndarray':
        """
        *Optional dependency `av` (imported as `av`) required*

        Transform the `av.VideoFrame` `frame` provided into a
        `numpy.ndarray` frame.
        """
        format = (
            'rgba'
            if do_include_alpha else
            'rgb24'
        )

        return frame.to_ndarray(format = format)
    
    @staticmethod
    @requires_dependency('av', 'yta_editor_utils', 'av')
    @requires_dependency('moderngl', 'yta_editor_utils', 'moderngl')
    @requires_dependency('numpy', 'yta_editor_utils', 'numpy')
    def videoframe_to_texture(
        frame: 'av.VideoFrame',
        moderngl_context: 'moderngl.Context',
        do_include_alpha: bool = True
    ) -> 'moderngl.Texture':
        """
        *Optional dependency `av` (imported as `av`) required*

        *Optional dependency `moderngl` (imported as `moderngl`) required*

        Transform the `av.VideoFrame` `frame` provided into a
        `moderngl.Texture` frame.
        """
        # 1. 'av.VideoFrame' to 'np.ndarray'
        frame = FrameHelper.videoframe_to_ndarray(
            frame = frame,
            do_include_alpha = do_include_alpha
        )

        # 2. 'np.ndarray' to 'moderngl.Texture'
        return FrameHelper.ndarray_to_texture(
            frame = frame,
            moderngl_context = moderngl_context,
            do_include_alpha = do_include_alpha
        )
    
    @staticmethod
    @requires_dependency('moderngl', 'yta_editor_utils', 'moderngl')
    @requires_dependency('numpy', 'yta_editor_utils', 'numpy')
    def texture_to_ndarray(
        frame: 'moderngl.Texture'
    ) -> Union['np.ndarray', bool]:
        """
        *Optional dependency `moderngl` (imported as `moderngl`) required*

        Transform the `moderngl.Texture` `frame` provided into
        a `np.ndarray` frame.

        (!) This method returns a tuple that includes the array
        but also a boolean indicating if the texture included
        alpha or not.
        """
        import numpy as np

        data = frame.read()
        w, h = frame.size

        data = np.frombuffer(data, dtype = np.uint8).reshape((h, w, frame.components))
        # frame = np.flipud(frame)
        # Similar to 'np.flipud(frame)'
        data = np.flip(data, axis = 0)

        """
        The 'frame.components defines if RGBA or RGB:
        - `frame.components=4` means RGBA
        - `frame.components=3` means RGB
        """
        return (data, frame.components == 4)

    @staticmethod
    @requires_dependency('av', 'yta_editor_utils', 'av')
    @requires_dependency('moderngl', 'yta_editor_utils', 'moderngl')
    @requires_dependency('numpy', 'yta_editor_utils', 'numpy')
    def texture_to_videoframe(
        frame: 'moderngl.Texture',
        pts: Union[int, None] = None,
        time_base: Union['Fraction', None] = None
    ) -> 'av.VideoFrame':
        """
        *Optional dependency `av` (imported as `av`) required*

        *Optional dependency `moderngl` (imported as `moderngl`) required*

        Transform the `moderngl.Texture` `frame` provided into
        a `av.VideoFrame` frame.
        """
        # 1. 'moderngl.Texture' to 'np.ndarray'
        frame, do_include_alpha = FrameHelper.texture_to_ndarray(
            frame = frame
        )

        # 2. 'np.ndarray' to 'av.VideoFrame'
        frame = FrameHelper.ndarray_to_videoframe(
            frame = frame,
            do_include_alpha = do_include_alpha
        )

        if pts is not None:
            frame.pts = pts

        if time_base is not None:
            frame.time_base = time_base

        return frame