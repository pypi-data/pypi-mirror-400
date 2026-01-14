"""
This module handles the creation of webhook subscriptions. It creates
a subscription to receive webhooks for a particular event_type.
"""
from k2connect import exceptions
from k2connect import json_builder
from k2connect import service
from k2connect import validation

WEBHOOK_SUBSCRIPTION_PATH = 'api/v1/webhook_subscriptions'


class WebhookService(service.Service):
    """
    The WebhookService class contains methods for the creation of a webhook
    subscription.
    Example:
        # initialize webhook service
        >>> k2-connect.WebhookService
        >>> k2-connect.create_subscription('buygoods_transaction_reversed',
        >>>................................'https://myapplication/webhooks',
        >>>................................os.getenv('SOME_UNCRACKABLE_SECRET'))

    """

    def __init__(self, base_url):
        """
        :param base_url:
        :type  base_url: str
        """
        super(WebhookService, self).__init__(base_url)

    def create_subscription(self, kwargs):
        """
        Creates a subscription to a webhook service.
        Returns a request response object < class, 'requests.models.Response'>
        :param bearer_token: Access token to be used to make calls to
        the Kopo Kopo API
        :param kwargs: The values constitute all user input.
        :type kwargs: dict
        :return: requests.models.Response
        """
        if 'access_token' not in kwargs:
            raise exceptions.InvalidArgumentError('Access Token not given.')
        if 'event_type' not in kwargs:
            raise exceptions.InvalidArgumentError('Event Type not given.')

        if 'webhook_endpoint' not in kwargs or \
                'scope' not in kwargs:
            raise exceptions.InvalidArgumentError('Invalid arguments for creating a Webhook Subscription.')

        if 'access_token' in kwargs:
            bearer_token = kwargs['access_token']
        if 'event_type' in kwargs:
            event_type = kwargs['event_type']
        if 'webhook_endpoint' in kwargs:
            webhook_endpoint = kwargs['webhook_endpoint']
        if 'scope' in kwargs:
            scope = kwargs['scope']
        if 'scope_reference' in kwargs:
            scope_reference = kwargs['scope_reference']

        # event types
        till_scope_event_types = ['b2b_transaction_received', 'buygoods_transaction_received', 'buygoods_transaction_reversed']
        company_scope_event_types = ['settlement_transfer_completed', 'm2m_transaction_received', 'customer_created']
        event_types_to_check = till_scope_event_types + company_scope_event_types

        # build subscription url
        subscription_url = self._build_url(WEBHOOK_SUBSCRIPTION_PATH)

        # define headers
        headers = dict(self._headers)

        # validate string arguments
        validation.validate_string_arguments(bearer_token,
                                             event_type,
                                             webhook_endpoint,
                                             scope)

        if 'scope_reference' in kwargs:
            validation.validate_string_arguments(scope_reference)

        headers['Authorization'] = 'Bearer ' + bearer_token + ''

        if not any(check in event_type for check in event_types_to_check):
            raise exceptions.InvalidArgumentError('Event type not recognized by k2-connect')

        if any(check in event_type for check in till_scope_event_types):
            if scope not in ['till', 'company']:
                raise exceptions.InvalidArgumentError('Invalid scope for given event type.')
            if ('scope_reference' not in kwargs or kwargs['scope_reference'] is None) and scope != 'company':
                raise exceptions.InvalidArgumentError('Scope reference not given.')

        if any(check in event_type for check in company_scope_event_types):
            if scope != 'company':
                raise exceptions.InvalidArgumentError('Invalid scope for given event type.')
            if 'scope_reference' in kwargs:
                raise exceptions.InvalidArgumentError('Invalid scope reference for given event type.')

        if scope == 'company':
            scope_reference = None
        # validate webhook endpoint
        validation.validate_url(webhook_endpoint)

        # define subscription payload
        subscription_payload = json_builder.webhook_subscription(event_type=event_type,
                                                                 webhook_endpoint=webhook_endpoint,
                                                                 scope=scope,
                                                                 scope_reference=scope_reference)

        return self._make_requests(headers=headers,
                                   method='POST',
                                   url=subscription_url,
                                   payload=subscription_payload)

    def webhook_status(self, bearer_token, query_url):
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
