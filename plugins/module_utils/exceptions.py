"""
Exceptions used by the management classes
"""
from __future__ import (absolute_import, division, print_function)


class SessionException(Exception):
    """
    Exception for session errors

    .. class:: SessionException
    """
    __metaclass__ = type


class InvalidCredentialsException(Exception):
    """
    Exception for invalid credentials

    .. class:: InvalidCredentialsException
    """
    __metaclass__ = type


class APILevelNotSupportedException(Exception):
    """
    Exception for unsupported API levels

    .. class:: APILevelNotSupportedException
    """
    __metaclass__ = type


class UnsupportedRequestException(Exception):
    """
    Exception for unsupported requests

    .. class:: UnsupportedRequest
    """
    __metaclass__ = type


class InvalidHostnameFormatException(Exception):
    """
    Exception for invalid hostname formats (non-FQDN)

    .. class:: InvalidHostnameFormatException
    """
    __metaclass__ = type


class UnsupportedFilterException(Exception):
    """
    Exception for unsupported filters

    .. class:: UnsupportedFilterException
    """
    __metaclass__ = type


class EmptySetException(Exception):
    """
    Exception for empty result sets

    .. class:: EmptySetException
    """
    __metaclass__ = type


class CustomVariableExistsException(Exception):
    """
    Exception for already existing custom variables

    .. class:: CustomVariableExistsException
    """
    __metaclass__ = type


class SnapshotExistsException(Exception):
    """
    Exception for already existing snapshots

    .. class:: SnapshotExistsException
    """
    __metaclass__ = type


class UnauthenticatedError(RuntimeError):
    """
    Exception for showing that a client wasn't able to authenticate itself

    .. class:: UnauthenticatedError
    """
    __metaclass__ = type


class SSLCertVerificationError(Exception):
    """
    Exception for invalid SSL certificates

    .. class:: SSLCertVerificationError
    """
    __metaclass__ = type
