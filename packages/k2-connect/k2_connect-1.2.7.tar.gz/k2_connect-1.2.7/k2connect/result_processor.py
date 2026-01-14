"""
This module handles the processing of response objects from k2-connect. It verifies
the authenticity of a response object by comparing the 'X-KopoKopo-Signature' with
a locally SHA-256 encrypted response body to validate the response.
"""
import hashlib
import hmac
import json

from k2connect import service
from k2connect import exceptions


class ResultProcessor(service.Service):
    """
    The RequestProcessor class containing methods to validate responses
    Example:
        >>>import k2connect
        >>>k2connect.initialize('sample_client_id', 'sample_client_secret', 'https://some_url.com/')
        >>> k2-connect.RequestProcessor
        >>> k2-connect.process(result)
    """
    def __init__(self, base_url, api_secret):
        """
        Initialize processor service with client id and client secret values for
        encryption with sha-256.
        """
        super(ResultProcessor, self).__init__(base_url)
        self._api_secret = api_secret

    def process(self, result):
        """
        Signs result body with a hmac signature. It the compares the resultant signature
        with the X-Kopo-Kopo signature from the headers of the result.
        If the signatures are the same, the result is valid.
        Returns a json formatted str containing content of the HTTP result.
        :param result: A HTTP result object
        :type result: requests.models.Response
        :return: str
        """
        if result is None or result == '':
            raise exceptions.InvalidArgumentError('Response cannot be empty')

        # define result body
        result_body = result.get_data()

        # define X-KopoKopo-Signature
        x_kopo_kopo_signature = result.headers.get('X-KopoKopo-Signature')

        # define hmac signature
        hmac_signature = generate_hmac_signature(bytes(self._api_secret, 'utf-8'), result_body)

        # compare signatures
        if hmac.compare_digest(hmac_signature, x_kopo_kopo_signature) is False:
            print("Hmac: ", hmac)
            print("Signature: ", x_kopo_kopo_signature)
            raise exceptions.InvalidArgumentError('Invalid result passed')
        return json.dumps(result.get_json(), sort_keys=True)


def generate_hmac_signature(api_secret, result_body):
    signature = hmac.new(api_secret, result_body, hashlib.sha256).hexdigest()
    return signature
