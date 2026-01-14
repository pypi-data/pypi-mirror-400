from yta_editor_common.frame.helper import FrameHelper
from yta_programming.decorators.requires_dependency import requires_dependency
from dataclasses import dataclass


@dataclass
class FrameBuffer:
    """
    *Dataclass*

    Dataclass to store the information about a buffer
    that we will need during the processing.

    This library could need one of these optional
    dependencies depending on what method you call to
    use it in the context you need it.
    - `av`
    - `numpy`
    - `moderngl`
    """

    @property
    def width(
        self
    ) -> int:
        """
        The width of the frame.
        """
        return self.size[0]
    
    @property
    def height(
        self
    ) -> int:
        """
        The height of the frame.
        """
        return self.size[1]

    def __init__(
        self,
        size: tuple[int, int],
        format: str,      # 'rgb', 'rgba'
        dtype: str,       # 'uint8', 'float32'
        is_data_normalized: bool,
    ):
        self.size: tuple[int, int] = size
        """
        The size of the frame, in pixels, expressed as a
        `(width, height)` tuple.
        """
        self.format: str = format
        """
        The format of the frame, that must be a value in
        between `rgb` and `rgba`.
        """
        self.dtype: str = dtype
        """
        The `dtype` of the frame (based on numpy).
        """
        self.is_data_normalized: bool = is_data_normalized
        """
        A flag to indicate if the values are set in the
        `[0, 1]` range or in the `[0, 255]`.
        """

        self._av_videoframe: 'av.VideoFrame' = None
        """
        The frame as a `av.VideoFrame`.
        """
        self._numpy_ndarray: 'np.ndarray' = None
        """
        The frame as a `numpy.ndarray`.
        """
        self._moderngl_texture: 'moderngl.Texture' = None
        """
        The frame as a `moderngl.Texture`.
        """

    @classmethod
    @requires_dependency('av', 'yta_editor_utils', 'av')
    def from_av_videoframe(
        cls,
        frame: 'av.VideoFrame'
    ) -> 'FrameBuffer':
        """
        Instantiate a `FrameBuffer` from a `av.VideoFrame`.
        """
        frame_buffer = cls(
            size = (frame.width, frame.height),
            format = 'rgba',
            dtype = 'uint8',
            is_data_normalized = False
        )

        frame_buffer._av_videoframe = frame

        return frame_buffer
    
    def as_numpy_ndarray(
        self,
        do_write: bool = False
    ) -> 'np.ndarray':
        """
        Get the frame but as a `numpy.ndarray`. This is
        meant for CPU use.

        This method will lazy load the value from the
        one that is available in the moment it is
        requested.

        If you will modify the return, set the `do_write`
        as `True`.

        The `do_write` parameter is to indicate that
        when you call the method with `do_write=True`
        is because you'll modify the instance and
        that one will become the new absolute truth,
        so the other types will be removed and this one,
        as returned as a reference, will be modified by
        your code and become the new valid one.
        """
        if self._numpy_ndarray is None:
            if self._av_videoframe is not None:
                self._numpy_ndarray = FrameHelper.videoframe_to_ndarray(
                    frame = self._av_videoframe,
                    do_include_alpha = 'a' in self.format
                )
            elif self._moderngl_texture is not None:
                self._numpy_ndarray = FrameHelper.texture_to_ndarray(
                    frame = self._numpy_ndarray
                )
            else:
                raise RuntimeError('No source to build `numpy.ndarray`')

        if do_write:
            self._av_videoframe = None
            self._moderngl_texture = None

        return self._numpy_ndarray
    
    def as_moderngl_texture(
        self,
        moderngl_context: 'moderngl.Context',
        do_write: bool = False
    ) -> 'moderngl.Texture':
        """
        Get the frame but as a `moderngl.Texture`. This
        is meant for GPU use.

        This method will lazy load the value from the
        one that is available in the moment it is
        requested.

        If you will modify the return, set the `do_write`
        as `True`.

        The `do_write` parameter is to indicate that
        when you call the method with `do_write=True`
        is because you'll modify the instance and
        that one will become the new absolute truth,
        so the other types will be removed and this one,
        as returned as a reference, will be modified by
        your code and become the new valid one.

        Remember that when obtaining this parameter
        """
        if self._moderngl_texture is None:
            if self._numpy_ndarray is not None:
                self._moderngl_texture = FrameHelper.ndarray_to_texture(
                    frame = self._numpy_ndarray,
                    # TODO: What do we do with the context? I think we should
                    # create one standalone context if this is None...
                    moderngl_context = moderngl_context,
                    do_include_alpha = 'a' in self.format
                )
            elif self._av_videoframe is not None:
                # TODO: If 'self._numpy_ndarray' is None we could set it here as
                # we are actually calculating it, right (?)
                self._moderngl_texture = FrameHelper.videoframe_to_texture(
                    frame = self._av_videoframe,
                    moderngl_context = moderngl_context,
                    do_include_alpha = 'a' in self.format
                )
            else:
                raise RuntimeError('No source to build `moderngl.Texture`')

        if do_write:
            self._av_videoframe = None
            self._numpy_ndarray = None

        return self._moderngl_texture
    
    def as_av_videoframe(
        self
    ) -> 'av.VideoFrame':
        """
        Get the frame but as a `av.VideoFrame`.

        This method will lazy load the value from the
        one that is available in the moment it is
        requested.
        """
        if self._av_videoframe is None:
            if self._numpy_ndarray is not None:
                self._av_videoframe = FrameHelper.ndarray_to_videoframe(
                    frame = self._numpy_ndarray,
                    do_include_alpha = 'a' in self.format
                )
            elif self._moderngl_texture is not None:
                # TODO: Should we be able to force alpha if the
                # texture doesn't include it (?)
                self._av_videoframe = FrameHelper.texture_to_videoframe(
                    frame = self._moderngl_texture
                )
            else:
                raise RuntimeError("No source to build VideoFrame")

        return self._av_videoframe


    
"""
A frame in HWC format (most common) is like this:
- `h, w = frame.shape[:2]`

If grayscale, is like this:
- `h, w = frame.shape`

If CHW, is like this:
- `c, h, w = frame.shape`
"""

"""
Puntos críticos (muy importantes en tu pipeline):

Flip vertical (OpenGL vs imagen)
OpenGL tiene el origen en bottom-left.
NumPy / PyAV esperan top-left.

Debes invertir verticalmente:
- `frame = np.flipud(frame)`

Número de canales:
- `texture.components`

3 → RGB
4 → RGBA

Tipo de dato
Por defecto:
- `dtype = uint8`

Si usas texturas float:
- `frame = np.frombuffer(data, dtype = np.float32)`

Contigüidad
Después del flipud, fuerza contigüidad:
- `frame = np.ascontiguousarray(frame)`
"""