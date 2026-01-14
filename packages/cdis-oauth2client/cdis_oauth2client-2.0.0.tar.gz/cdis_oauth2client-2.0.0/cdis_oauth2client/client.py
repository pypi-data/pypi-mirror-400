"""
cdis_oauth2client.client

Defines the OAuth2Client class for use by CDIS internal microservices.
"""

import urllib.request, urllib.parse, urllib.error

from cdispyutils.log import get_logger
import requests

from .exceptions import OAuth2Error


_PDC = "https://bionimbus-pdc.opensciencedatacloud.org/api/oauth2/"


class OAuth2Client(object):
    """
    OAuth2 client that can be used by CDIS internal microservices.
    """

    logger = get_logger("OAuth2Client")

    def __init__(
        self,
        client_id,
        client_secret,
        redirect_uri,
        oauth_provider=_PDC,
        internal_oauth_provider=None,
        scope="user",
    ):
        """
        According to the Flask-OAuthlib docs, the Client should have (at least)
        the following properties:

        `client_id`
            A random string.

        `client_secret`
            A random string.

        `client_type`
            A string representing if 'it is confidential' (quote from the docs)

        `redirect_uris`
            A list of redirect uris.

        `default_redirect_uri`
            One of the redirect uris to default to.

        `default_scopes`
            The default scopes of the client.

        An example using SQLAlchemy can be found here:
        https://flask-oauthlib.readthedocs.io/en/latest/oauth2.html
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.oauth_provider = oauth_provider
        self.internal_oauth = internal_oauth_provider or oauth_provider
        self.redirect_uri = redirect_uri
        self.scope = scope

    @property
    def authorization_url(self):
        """Return the URL at which the authorization can be obtained."""
        tail = urllib.parse.urlencode(
            {
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "response_type": "code",
                "scope": self.scope,
            }
        )
        return urllib.parse.urljoin(self.oauth_provider, "authorize") + "?" + tail

    def _post_to_internal_oauth(self, data):
        """
        Post data to the URL at ``self.internal_oauth``.

        This is used for retrieving or refreshing the OAuth credentials (see
        ``get_token`` and ``refresh_token``, which also have examples for what
        ``data`` should look like).
        """
        try:
            url = urllib.parse.urljoin(self.internal_oauth, "token")
            return requests.post(url, data=data).json()
        except requests.RequestException as e:
            msg = "request failed to reach oauth provider: " + str(e.message)
            self.logger.exception(msg)
            return {"error": msg}
        except Exception as e:  # pylint: disable=broad-except
            msg = "unexpected error trying to reach oauth provider: " + str(e.message)
            self.logger.exception(msg)
            return {"error": msg}

    def get_token(self, code):
        """
        Retrieve the oauth credentials.

        An example of the credentials returned:

            {
                u'access_token': u'9ydWQi1SqGU82hAGf8M0JoNJbXhxQ1',
                u'expires_in': 3600, u'refresh_token':
                u'Ll6PfksjrCSJHtkEQV41mRRbR4tUxU', u'scope': u'user',
                u'token_type': u'Bearer'
            }

        :param code: usually flask.request.args.get('code')
        :type code: str
        :return: dictionary of OAuth credentials (see above)
        :rtype: dict
        """
        # Formulate the data for posting to the OAuth provider.
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }
        return self._post_to_internal_oauth(data)

    def get_access_token(self, code):
        """
        Get specifically the access_token from the OAuth token response.
        """
        token_response = self.get_token(code)
        access_token = token_response.get("access_token")
        if not access_token:
            raise OAuth2Error(
                message="did not receive access token", json=token_response
            )
        return access_token

    def refresh_token(self, refresh_token):
        """
        Refresh the OAuth access token.

        The credentials returned should be the same as the example in
        ``get_token``.
        """
        # Formulate the data for posting to the OAuth provider.
        data = {
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "redirect_uri": self.redirect_uri,
        }
        return self._post_to_internal_oauth(data)
