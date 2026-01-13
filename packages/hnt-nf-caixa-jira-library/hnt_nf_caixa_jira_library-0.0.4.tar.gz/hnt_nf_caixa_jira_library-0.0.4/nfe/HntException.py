class HntException(Exception):
    def __init__(self, message, cause=None):
        self.message = message
        self.cause = cause

    def __str__(self):
        if self.cause:
            return f'HNTException: {self.message} caused by {self.cause}'
        else:
            return f'HNTException: {self.message}'

    def __cause__(self):
        return self.cause