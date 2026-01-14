from yta_editor_common.frame.core import FrameBuffer
from yta_editor_common.frame.core.domain import FrameBufferDomain
from yta_editor_common.frame.registry import register_domain_converter


# TODO: Add the 'requires_dependency' for 'moderngl' (?)
# TODO: Add the 'requires_dependency' for 'numpy' (?)
def cpu_to_gpu(
    frame: FrameBuffer,
    moderngl_context: 'moderngl.Context'
) -> FrameBuffer:
    """
    Method to convert from CPU (`numpy`) to GPU
    (`moderngl.Texture`).
    """
    from yta_editor_common.frame.helper import FrameHelper

    h, w = frame.payload.shape[:2]
    format = frame.format
    dtype = frame.dtype
    is_normalized = frame.is_normalized
    domain = FrameBufferDomain.GPU
    payload = FrameHelper.ndarray_to_texture(
        frame = frame.payload,
        moderngl_context = moderngl_context,
        do_include_alpha = True
    )

    return FrameBuffer(
        size = (w, h),
        format = format,
        dtype = dtype,
        is_normalized = is_normalized,
        domain = domain,
        payload = payload
    )

    import moderngl

    arr = frame.payload
    h, w = arr.shape[:2]

    tex = moderngl_context.texture(
        (w, h),
        components = 4,
        data = arr.tobytes()
    )

    return FrameBuffer(
        size = (w, h),
        format = frame.format,
        dtype = frame.dtype,
        is_normalized = frame.is_normalized,
        domain = FrameBufferDomain.GPU,
        payload = tex
    )

register_domain_converter(FrameBufferDomain.CPU, FrameBufferDomain.GPU, cpu_to_gpu)
