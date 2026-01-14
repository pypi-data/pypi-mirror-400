from yta_editor_common.frame.core import FrameBuffer
from yta_editor_common.frame.helper import FrameHelper
from yta_editor_common.frame.core.domain import FrameBufferDomain
from yta_editor_common.frame.registry import register_domain_converter


# TODO: Add the 'requires_dependency' for 'av' (?)
# TODO: Add the 'requires_dependency' for 'numpy' (?)
def media_to_cpu(
    frame: FrameBuffer
) -> FrameBuffer:
    """
    Method to convert from Media (`av.VideoFrame`) to
    CPU (`numpy`).
    """
    size = frame.size
    format = frame.format
    dtype = 'uint8'
    is_normalized = False
    domain = FrameBufferDomain.CPU
    payload = FrameHelper.videoframe_to_ndarray(
        frame = frame.payload,
        do_include_alpha = True
    )

    return FrameBuffer(
        size = size,
        format = format,
        dtype = dtype,
        is_normalized = is_normalized,
        domain = domain,
        payload = payload
    )

    arr = frame.payload.to_ndarray(format = 'rgba')

    return FrameBuffer(
        size = frame.size,
        format = frame.format,
        dtype = 'uint8',
        normalized = False,
        domain = FrameBufferDomain.CPU,
        payload = arr
    )

# TODO: Add the 'requires_dependency' for 'moderngl' (?)
# TODO: Add the 'requires_dependency' for 'numpy' (?)
def gpu_to_cpu(
    frame: FrameBuffer
) -> FrameBuffer:
    """
    Method to convert from GPU (`moderngl.Texture`) to
    CPU (`numpy`).
    """
    w, h = frame.payload.size
    dtype = 'uint8'
    is_normalized = False
    domain = FrameBufferDomain.CPU
    payload, has_alpha = FrameHelper.texture_to_ndarray(
        frame = frame.payload
    )[0]
    format = (
        'rgba'
        if has_alpha else
        'rgb24'
    )

    return FrameBuffer(
        size = (w, h),
        format = format,
        dtype = dtype,
        is_normalized = is_normalized,
        domain = domain,
        payload = payload
    )

    import numpy as np

    tex = frame.payload
    data = np.frombuffer(tex.read(), dtype=np.uint8)
    w, h = tex.size
    arr = data.reshape((h, w, tex.components))
    arr = np.flipud(arr)
    return FrameBuffer(
        size=(w, h),
        format='rgba',
        dtype='uint8',
        is_normalized = False,
        domain=FrameBufferDomain.CPU,
        payload=arr
    )

register_domain_converter(FrameBufferDomain.MEDIA, FrameBufferDomain.CPU, media_to_cpu)
register_domain_converter(FrameBufferDomain.GPU, FrameBufferDomain.CPU, gpu_to_cpu)
