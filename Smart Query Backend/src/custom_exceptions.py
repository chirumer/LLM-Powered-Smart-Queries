from enum import Enum

class ApplicationException(Exception):
    def __init__(self, message):
        self.message = message

class QueryGenerationFail(Exception):

    class Reason(Enum):
        NOT_ENOUGH_CONTEXT = 1

    def __init__(self, reason):
        self.reason = reason