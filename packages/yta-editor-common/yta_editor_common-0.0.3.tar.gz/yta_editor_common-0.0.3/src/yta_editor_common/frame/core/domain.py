from yta_constants.enum import YTAEnum as Enum


class FrameBufferDomain(Enum):
    """
    Enum to indicate the domain of a `FrameBuffer` instance.
    """

    CPU = 'cpu'
    """
    The CPU domain, which is leaded by `numpy`.
    """
    GPU = 'gpu'
    """
    The GPU domain, which is leaded by `moderngl`.
    """
    MEDIA = 'media'
    """
    TODO: I think this one means `av.VideoFrame`.
    """
