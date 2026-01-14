class MuxedConnError(Exception):
    pass


class MuxedConnUnavailable(MuxedConnError):
    pass


class MuxedStreamError(Exception):
    pass


class MuxedStreamReset(MuxedStreamError):
    pass


class MuxedStreamEOF(MuxedStreamError, EOFError):
    pass


class MuxedStreamClosed(MuxedStreamError):
    pass

class RawConnError(Exception):
    pass

class IncompleteReadError(Exception):
    """Fewer bytes were read than requested."""