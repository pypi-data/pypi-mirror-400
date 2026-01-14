from yta_editor_common.frame.core.domain import FrameBufferDomain
from typing import Union
from dataclasses import dataclass


@dataclass
class FrameBuffer:
    """
    *Dataclass*

    Dataclass to store the information about a buffer
    that we will need during the processing.
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
        is_normalized: bool,
        domain: FrameBufferDomain,
        payload: object
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
        self.is_normalized: bool = is_normalized
        """
        A flag to indicate if the values are set in the
        `[0, 1]` range or in the `[0, 255]`.
        """
        self.domain: FrameBufferDomain = domain
        """
        The domain of the `FrameBuffer` instance.
        """
        self.payload: Union['av.VideoFrame', 'np.ndarray', 'moderngl.Texture'] = payload
        """
        The frame itself, the data.
        """

    def to_cpu(
        self
    ):
        """
        Convert the current frame to CPU.
        """
        from yta_editor_common.frame.registry import frame_buffer_to_domain
        from yta_editor_common.frame.core.domain import FrameBufferDomain

        return frame_buffer_to_domain(
            frame_buffer = self,
            target_domain = FrameBufferDomain.CPU
        )

    def to_gpu(
        self,
        moderngl_context: 'moderngl.Context'
    ):
        """
        Convert the current frame to GPU by using the
        `moderngl_context` provided.
        """
        from yta_editor_common.frame.registry import frame_buffer_to_domain
        from yta_editor_common.frame.core.domain import FrameBufferDomain

        return frame_buffer_to_domain(
            frame = self,
            target_domain = FrameBufferDomain.GPU,
            moderngl_context = moderngl_context
        )

