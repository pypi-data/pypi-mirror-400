"""

This module handles k2-connect receive MPESA payments service. It facilitates
the reception of payments from MPESA users. It creates requests for the reception
of MPESA payments. Succeeding a MPESA payment request, it queries the status of the
transaction.
"""
from k2connect import exceptions
from k2connect import json_builder
from k2connect import k2_requests
from k2connect import service
from k2connect import validation

POLLING_PATH = 'api/v1/polling'


class PollingService(service.Service):
    """
    The ReceivePaymentsService class containing methods to create requests for
    MPESA payments:
    Example:
        >>>import k2connect
        >>>k2connect.initialize('sample_client_id', 'sample_client_secret', 'https://some_url.com/')
        >>>polling = k2connect.PollingService
        >>>polling_request = polling.create_polling_request('bearer_token',
        >>>....................................................................'callback_url',
        >>>....................................................................'currency',
        >>>....................................................................'first_name',
        >>>....................................................................'last_name',
        >>>....................................................................'payment_channel')

    To check payment request status:
    Example:
        >>>polling_status = polling.polling_request_status('bearer_token',
        >>>......................................................'query_url')

    To check payment request location:
    Example:
        >>>polling_location = polling.polling_request_location('response')
    """

    def __init__(self, base_url):
        """
        :param base_url: The domain to use in the library
        :type  base_url: str
        """
        super(PollingService, self).__init__(base_url=base_url)

    # noinspection PyArgumentList
    def create_polling_request(self, kwargs):
        """
        Creates a request for the reception of payments from MPESA users.
        Returns a request response object < class, 'requests.models.Response'>
        :param kwargs: The values constitute all user input.
        :type kwargs: dict
        :return: requests.models.Response
        """
        if 'access_token' not in kwargs:
            raise exceptions.InvalidArgumentError('Access Token not given.')

        if 'scope' not in kwargs or \
                'scope_reference' not in kwargs or \
                'from_time' not in kwargs or \
                'to_time' not in kwargs or \
                'callback_url' not in kwargs:
            raise exceptions.InvalidArgumentError('Invalid arguments for creating Polling Request.')

        # iterate through kwargs
        if 'access_token' in kwargs:
            bearer_token = kwargs['access_token']
        if 'scope' in kwargs:
            scope = kwargs['scope']
        if 'scope_reference' in kwargs:
            scope_reference = kwargs['scope_reference']
        if 'from_time' in kwargs:
            from_time = kwargs['from_time']
        if 'to_time' in kwargs:
            to_time = kwargs['to_time']
        if 'callback_url' in kwargs:
            callback_url = kwargs['callback_url']

        # define headers
        headers = dict(self._headers)

        # validate bearer_token
        validation.validate_string_arguments(bearer_token)

        # add bearer token
        headers['Authorization'] = 'Bearer ' + bearer_token + ''

        # build polling request url
        polling_request_url = self._build_url(POLLING_PATH)

        # define links JSON object
        polling_request_links = json_builder.links(callback_url=callback_url)

        # define MPESA payment request JSON object
        polling_request_payload = json_builder.polling(scope=scope,
                                                       scope_reference=scope_reference,
                                                       from_time=from_time,
                                                       to_time=to_time,
                                                       polling_links=polling_request_links)
        return self._make_requests(headers=headers,
                                   method='POST',
                                   url=polling_request_url,
                                   payload=polling_request_payload)

    def polling_request_status(self,
                               bearer_token,
                               query_url):
        """
        Returns a JSON object result containing the payment request status.
        :param bearer_token: Access token to be used to make calls to
        the Kopo Kopo API
        :type bearer_token: str
        :param query_url: URL to which status query is made.
        :type query_url: str
        :return str
        """
        return self._query_transaction_status(bearer_token=bearer_token,
                                              query_url=query_url)

    @staticmethod
    def polling_request_location(response):
        """
        Returns location of the receive mpesa transaction result as returned in the headers of the
        response body.
        :param response: response object from a HTTP request
        :type response: requests.models.Response
        :return str
        """
        return service.k2_requests.get_location(response)
