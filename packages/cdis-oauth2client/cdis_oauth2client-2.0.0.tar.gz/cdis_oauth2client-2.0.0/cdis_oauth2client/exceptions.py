"""
cdis_oauth2client.exceptions

Provides the OAuth2Error exception that represents some problem with the
authentication.
"""


class OAuth2Error(Exception):
    """
    An exception to represent a problem with OAuth2 authentication.

    See :py:func:``authorize`` in :py:mod:``oauth2`` for usage examples.
    """

    def __init__(self, message="", json=None):
        super(OAuth2Error, self).__init__(message)
        self.message = message
        self.code = 400
        self.json = json
