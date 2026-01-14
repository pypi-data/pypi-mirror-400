"""
This module handles HTTP requests for the k2-connect library.
It defines all base requirements for requests made by different
k2-connect services. Furthermore, it handles the access of specific
resources contained in responses of HTTP requests.
"""
import requests
from urllib.parse import urlparse
from k2connect import exceptions
from k2connect import validation


class Requests:
    """
    Performs k2-connect HTTP requests.
    Retrieves values found in k2-connect response objects.
    """

    def __init__(self):
        """
        Initializes function arguments and other variables necessary
        for class and its subclasses.

        :param bearer_token: Access token to be used to make calls to the Kopo Kopo API
        :type  bearer_token: str
        """
        self._headers = {
            'Accept': 'application/vnd.kopokopo.v4.hal+json',
            'Content-Type': 'application/json'
        }

    @staticmethod
    def __get_request(headers, params, url):
        """
        Returns http response.

        :param url: URL to which GET request is sent.
        :type url: str
        :param headers: Headers for GET requests
        :type headers: dict
        :param params: Dictionary, list of tuples or bytes to send
        in the body of the :class:`Request`.
        :type params:
        :return: 'requests.models.Response'
        """
        response = requests.get(
            headers=headers,
            params=params,
            url=url)
        return response

    @staticmethod
    def __post_request(headers, url, payload, data):
        """
        Returns http response.

        :param url: URL to which POST request is sent.
        :type url: str
        :param headers: Headers for POST requests.
        :type headers: str (json)
        :param payload: Payload for POST request
        :type payload: str (json)
        :param data: Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
        :return: 'requests.models.Response'
        """

        response = requests.post(
            headers=headers,
            json=payload,
            data=data,
            url=url,
        )

        return response

    def _make_requests(self,
                       headers,
                       method,
                       url,
                       data=None,
                       payload=None,
                       params=None):
        """
        Returns JSON payload.
        :param headers: Headers for HTTP request
        :type headers: str (JSON)
        :param method: Method for HTTP request (GET, POST)
        :type method str
        :param url: URL to which HTTP request is sent
        :type url: str
        :param data: Dictionary, list of tuples or bytes to send
        in the body of the :class:`Request`.
        :param payload: Payload for HTTP request
        :type payload: str (JSON)
        :param params: Query parameters for a HTTP request
        :type params: str (JSON)
        :return: str (JSON)
        """
        if validation.validate_url(url) is True:
            if method == 'GET':
                response = self.__get_request(url=url,
                                              headers=headers,
                                              params=params)
            elif method == 'POST':
                response = self.__post_request(url=url,
                                               headers=headers,
                                               payload=payload,
                                               data=data)
            else:
                raise exceptions.InvalidArgumentError('Method not recognized by k2-connect')
            # define status code to check
            status_code = response.status_code

            if 200 <= status_code <= 300:
                if 'oauth' in urlparse(url).path or method == 'GET':
                    return response.json()
                response_location = response.headers.get('location')
                return response_location
            response_error = {
                'error_code': status_code,
                'error_content': response.text
            }
            raise exceptions.K2Error(response_error)
        return exceptions.K2Error

    def _query_transaction_status(self,
                                  bearer_token,
                                  query_url):
        """
        Returns a JSON object result containing the transaction status.
        :param bearer_token: Access token to be used to make calls to
        the Kopo Kopo API
        :type bearer_token: str
        :param query_url: URL to which status query is made.
        :type query_url: str
        :return: str
        """
        # define headers
        _headers = dict(self._headers)

        # check bearer token
        validation.validate_string_arguments(bearer_token, query_url)
        # add bearer token
        _headers['Authorization'] = 'Bearer ' + bearer_token + ''

        # validate url
        validation.validate_url(query_url)

        return self._make_requests(url=query_url,
                                   method='GET',
                                   headers=_headers)


def get_location(response):
    """
    Returns location of a transaction as returned in the header of a response object.
    :param response: response object succeeding a successful post request.
    :type response: requests.models.Response
    :return: str
    """
    resource_location = response.headers('location')
    return resource_location
