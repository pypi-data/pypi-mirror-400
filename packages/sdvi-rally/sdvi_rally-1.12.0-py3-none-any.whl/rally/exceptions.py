""" Rally Exception support.

Provides Exceptions for Rally

Import example:

>>> from rally import exceptions
"""
__all__ = [
    'RallyError',
    'RallyApiError',
    'AlreadyExists',
    'NotFound',
    'JobRetryException'
]


class RallyError(Exception):
    """ Generic Rally error """
    def __init__(self, error):
        super().__init__(error)


class RallyApiError(RallyError):
    """ Rally API-specific error """
    def __init__(self, error):
        resp = getattr(error, 'response', None)
        self.code = getattr(resp, 'status_code', None)
        super().__init__(resp.text if resp is not None else str(error))


class AlreadyExists(RallyError):
    """ Raised when the Rally resource already exists """
    def __init__(self, resource):
        super().__init__(f'"{resource}" already exists')


class NotFound(RallyError):
    """ Raised when the Rally resource is not found """
    def __init__(self, resource):
        super().__init__(f'"{resource}" not found')


class JobRetryException(Exception):
    """ Raise this exception to fail this job and retry it later """
    def __init__(self, message, hold_time=None):
        """
        :param message: Explanation of the error
        :type message: str
        :param hold_time: Minimum hold time (in seconds) before retrying the job
        :type hold_time: int, optional
        """

        super().__init__(message)
        self.retry = True
        self.holdTime = hold_time
