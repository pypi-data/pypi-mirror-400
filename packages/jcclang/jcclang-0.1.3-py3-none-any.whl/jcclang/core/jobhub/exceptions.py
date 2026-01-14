from .types import StreamResultCode


class OpenJobStreamError(Exception):
    def __init__(self, code: StreamResultCode):
        self.code = code
