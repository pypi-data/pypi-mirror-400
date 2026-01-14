"""Handles custom exceptions"""


class K2Error(Exception):
    """Base exception for all errors raised by the K2-Connect library"""

    def __init__(self, error=None):
        if error is None:
            # default error message
            error = "An error has occurred  in the k2-connect library"
        super(K2Error, self).__init__(error)


class InvalidArgumentError(K2Error):
    """The argument passed is invalid, pass message to error description"""
