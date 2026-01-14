_ADAPTERS = {}

def register_domain_converter(
    source_domain: 'FrameBufferDomain',
    destination_domain: 'FrameBufferDomain',
    func
):
    """
    Register a `FrameBufferDomain` converter to go
    transform a `FrameBuffer` the `source_domain`
    domain to the `destination_domain` domain.
    """
    _ADAPTERS[(source_domain, destination_domain)] = func

def frame_buffer_to_domain(
    frame_buffer: 'FrameBuffer',
    target_domain: 'FrameBufferDomain',
    **kwargs
):
    """
    Convert the `frame_buffer` provided to the
    `target_domain` given, if possible.
    """
    if frame_buffer.domain == target_domain:
        return frame_buffer

    key = (frame_buffer.domain, target_domain)
    if key not in _ADAPTERS:
        raise RuntimeError(f'No adapter {key}')

    return _ADAPTERS[key](frame_buffer, **kwargs)
