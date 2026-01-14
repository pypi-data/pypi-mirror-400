"""
This module handles OAuth authentication requests using client credentials
i.e. client id and client secret.Once authenticated, the module responds
with a payload containing an access token and its expiry duration. The
access (Bearer) token will be used to authorize the user when requesting
access to k2 resources .
"""
from urllib.parse import urlencode
from k2connect import service
from k2connect import validation

# path for authorization requests
AUTHORIZATION_PATH = 'oauth/token'
REVOKE_PATH = 'oauth/revoke'
INTROSPECT_PATH = 'oauth/introspect'
TOKEN_INFO_PATH = 'oauth/token/info'


class TokenService(service.Service):
    """
    The TokenService class containing methods to request access tokens.
    Example:
        >>>import k2connect
        >>>k2connect.initialize('sample_client_id', 'sample_client_secret', 'https://some_url.com/')
        >>>authenticator = k2-connect.Tokens
        >>>authenticator.request_access_token()
    Get access token and expiry duration
    Example:
        >>>token_response = authenticator.request_access_token()
        >>>access_token = get_access_token(token_service_response)
        >>>expiry_duration = get_token_expiry_duration(token_service_response)
    """

    def __init__(self,
                 base_url,
                 client_id,
                 client_secret):
        """
        Initializes class and inherits all necessary values
        from super class initialization as passed in the library
        initialization function.
        :param base_url: The domain to use in the library.
        :type base_url: str
        :param client_id: Identifier for the k2 user.
        :type client_id: str
        :param client_secret: Secret key for k2 user.
        :type client_secret: str
        """
        validation.validate_string_arguments(base_url,
                                             client_id,
                                             client_secret)

        super(TokenService, self).__init__(base_url)

        self._client_id = client_id
        self._client_secret = client_secret

    def request_access_token(self):
        """
        Returns response object with payload containing access token and
        expiry time.
        """

        # build URL for token request
        url = self._build_url(AUTHORIZATION_PATH)

        # redefine headers for token request
        headers = dict(self._headers)

        # add content-type
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

        # define client credentials payload
        client_credentials_payload = {
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'grant_type': 'client_credentials',
        }

        # url-encode payload
        data = urlencode(client_credentials_payload)

        # request access token and expiry duration
        access_token_request = self._make_requests(data=data, headers=headers, method='POST', url=url)

        return access_token_request

    def revoke_access_token(self, access_token):
        """
        Returns response object with payload containing access token and
        expiry time.
        """

        # build URL for token request
        url = self._build_url(REVOKE_PATH)

        # redefine headers for token request
        headers = dict(self._headers)

        # add content-type
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

        # define client credentials payload
        client_credentials_payload = {
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'token': access_token,
        }

        # url-encode payload
        data = urlencode(client_credentials_payload)

        # request access token and expiry duration
        access_token_request = self._make_requests(data=data, headers=headers, method='POST', url=url)

        return access_token_request

    def introspect_access_token(self, access_token):
        """
        Returns response object with payload containing access token and
        expiry time.
        """

        # build URL for token request
        url = self._build_url(INTROSPECT_PATH)

        # redefine headers for token request
        headers = dict(self._headers)

        # add content-type
        headers['Content-Type'] = 'application/json'

        # define client credentials payload
        client_credentials_payload = {
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'token': access_token,
        }

        # request access token and expiry duration
        access_token_request = self._make_requests(payload=client_credentials_payload, headers=headers, method='POST', url=url)

        return access_token_request

    def request_token_info(self, access_token):
        """
        Returns response object with payload containing access token and
        expiry time.
        """

        # build URL for token request
        url = self._build_url(TOKEN_INFO_PATH)

        # redefine headers for token request
        headers = dict(self._headers)

        # add access_token
        headers['Authorization'] = "Bearer " + access_token

        # request access token and expiry duration
        access_token_request = self._make_requests(headers=headers, method='GET', url=url)

        return access_token_request

    @staticmethod
    def get_access_token(response):
        """Returns a str containing access token"""
        # get access toke value
        access_token = response.get('access_token')
        return access_token

    @staticmethod
    def get_token_expiry_duration(response):
        """Return duration to expiry of access token"""
        token_expiry_duration = response.json().get('expires_in')
        return token_expiry_duration
