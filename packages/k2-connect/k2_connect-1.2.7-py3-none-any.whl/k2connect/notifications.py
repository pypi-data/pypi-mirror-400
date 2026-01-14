"""
This module handles transfer of funds to pre-approved settlement accounts. It creates
verified settlement bank accounts. Once an account to which funds can be settled is available,
it creates blind and targeted settlement transactions.
Blind transfers are made to the default settlement account defined upon k2 customer acquisition,
targeted transfers are made to a defined destination account.
"""
from k2connect import json_builder, exceptions, service, validation

TRANSACTION_NOTIFICATIONS_PATH = 'api/v1/transaction_sms_notifications'


class NotificationService(service.Service):
    """
    The TransferService class containing methods for creation of settlement accounts:
    Example:
        # initialize transfer service
        >>> k2connect.TransferService
        >>> k2connect.add_bank_settlement_account('Arya Stark',
        >>>.....................................'45164-IRON BANK',
        >>>.....................................'78491631254523',
        >>>.....................................'564123456987845')
    """

    def __init__(self, base_url):
        """
        Initializes transfer services with the base_url as an argument.
        :param base_url:
        :type  base_url: str
        """
        super(NotificationService, self).__init__(base_url)

    def send_transaction_sms_notification(self, kwargs):
        """
        Creates a transaction sms notification.
        Returns a request response object < class, 'requests.models.Response'>
        :return: requests.models.Response
        """
        if 'access_token' not in kwargs:
            raise exceptions.InvalidArgumentError('Access Token not given.')

        if 'webhook_event_reference' not in kwargs or \
                'message' not in kwargs or \
                'callback_url' not in kwargs:
            raise exceptions.InvalidArgumentError('Invalid arguments for creating Transaction SMS Notification.')

        # iterate through kwargs
        if 'access_token' in kwargs:
            bearer_token = kwargs['access_token']
        if 'webhook_event_reference' in kwargs:
            webhook_event_reference = kwargs['webhook_event_reference']
        if 'message' in kwargs:
            message = kwargs['message']
        if 'callback_url' in kwargs:
            callback_url = kwargs['callback_url']

        # build url
        create_transaction_sms_notification_url = self._build_url(TRANSACTION_NOTIFICATIONS_PATH)

        # define headers
        headers = dict(self._headers)

        # validate string arguments
        validation.validate_string_arguments(bearer_token, webhook_event_reference, message, callback_url)

        notification_links = json_builder.links(callback_url=callback_url)

        # add authorization to headers
        headers['Authorization'] = 'Bearer ' + bearer_token + ''
        # define create bank settlement account payload
        create_transaction_sms_notification_payload = json_builder.transaction_sms_notification(webhook_event_reference=webhook_event_reference,
                                                                                                message=message,
                                                                                                notification_links=notification_links)
        return self._make_requests(headers=headers,
                                   method='POST',
                                   url=create_transaction_sms_notification_url,
                                   payload=create_transaction_sms_notification_payload)

    def transaction_notification_status(self,
                                    bearer_token,
                                    query_url):
        """
        Returns a JSON object result containing the transaction status.
        :param bearer_token: Access token to be used to make calls to
        the Kopo Kopo API.
        :type bearer_token: str
        :param query_url: URL to which status query is made.
        :type query_url: str
        :return str
        """
        return self._query_transaction_status(bearer_token=bearer_token,
                                              query_url=query_url)

    @staticmethod
    def transaction_notification_location(response):
        """
        Returns location of the transfers transaction result as returned in the headers of the
        response body.
        :param response: response object from a HTTP request
        :type response: requests.models.Response
        :return str
        """
        return service.k2_requests.get_location(response)
