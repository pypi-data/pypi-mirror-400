"""
This module handles transfer of funds to pre-approved settlement accounts. It creates
verified settlement bank accounts. Once an account to which funds can be settled is available,
it creates blind and targeted settlement transactions.
Blind transfers are made to the default settlement account defined upon k2 customer acquisition,
targeted transfers are made to a defined destination account.
"""
from k2connect import json_builder, exceptions, service, validation

TRANSFER_PATH = 'api/v1/settlement_transfers'
SETTLEMENT_BANK_ACCOUNTS_PATH = 'api/v1/merchant_bank_accounts'
SETTLEMENT_MOBILE_ACCOUNTS_PATH = 'api/v1/merchant_wallets'


class TransferService(service.Service):
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
        Initializes transfer services with the bearer token as an argument.
        This feature allows the developer to refresh the access token
        at any point in their codebase.
        :param bearer_token: Access token to be used to make calls to
        the Kopo Kopo API
        :type  bearer_token: str
        """
        super(TransferService, self).__init__(base_url)

    def add_bank_settlement_account(self, kwargs):
        """
        Creates a verified settlement bank account.
        Returns a request response object < class, 'requests.models.Response'>
        :return: requests.models.Response
        """
        if 'access_token' not in kwargs:
            raise exceptions.InvalidArgumentError('Access Token not given.')

        if 'settlement_method' not in kwargs or \
                'account_name' not in kwargs or \
                'account_number' not in kwargs or \
                'bank_branch_ref' not in kwargs:
            raise exceptions.InvalidArgumentError('Invalid arguments for creating Bank Settlement Account.')

        # iterate through kwargs
        if 'access_token' in kwargs:
            bearer_token = kwargs['access_token']
        if 'settlement_method' in kwargs:
            settlement_method = kwargs['settlement_method']
        if 'account_name' in kwargs:
            account_name = kwargs['account_name']
        if 'account_number' in kwargs:
            account_number = kwargs['account_number']
        if 'bank_branch_ref' in kwargs:
            bank_branch_ref = kwargs['bank_branch_ref']

        # build url
        create_bank_settlement_account_url = self._build_url(SETTLEMENT_BANK_ACCOUNTS_PATH)

        # define headers
        headers = dict(self._headers)

        # validate string arguments
        validation.validate_string_arguments(bearer_token,
                                             settlement_method,
                                             account_name,
                                             bank_branch_ref,
                                             account_number)

        # add authorization to headers
        headers['Authorization'] = 'Bearer ' + bearer_token + ''
        # define create bank settlement account payload
        create_bank_settlement_account_payload = json_builder.bank_settlement_account(settlement_method=settlement_method,
                                                                                      account_name=account_name,
                                                                                      account_number=account_number,
                                                                                      bank_branch_ref=bank_branch_ref)
        return self._make_requests(headers=headers,
                                   method='POST',
                                   url=create_bank_settlement_account_url,
                                   payload=create_bank_settlement_account_payload)

    def add_mobile_wallet_settlement_account(self, kwargs):
        """
        Creates a verified settlement bank account.
        Returns a request response object < class, 'requests.models.Response'>
        :param kwargs: The values constitute all user input.
        :type kwargs: dict
        :return: requests.models.Response
        """
        if 'access_token' not in kwargs:
            raise exceptions.InvalidArgumentError('Access Token not given.')

        if 'first_name' not in kwargs or \
                'last_name' not in kwargs or \
                'phone_number' not in kwargs or \
                'network' not in kwargs:
            raise exceptions.InvalidArgumentError('Invalid arguments for creating Outgoing Pay.')

        # iterate through kwargs
        if 'access_token' in kwargs:
            bearer_token = kwargs['access_token']
        if 'first_name' in kwargs:
            first_name = kwargs['first_name']
        if 'last_name' in kwargs:
            last_name = kwargs['last_name']
        if 'phone_number' in kwargs:
            phone_number = kwargs['phone_number']
        if 'network' in kwargs:
            network = kwargs['network']

        # build url
        create_mobile_wallet_settlement_account_url = self._build_url(SETTLEMENT_MOBILE_ACCOUNTS_PATH)

        # define headers
        headers = dict(self._headers)

        # validate string arguments
        validation.validate_string_arguments(bearer_token,
                                             first_name,
                                             last_name,
                                             phone_number,
                                             network)

        validation.validate_phone_number(phone_number)

        # add authorization to headers
        headers['Authorization'] = 'Bearer ' + bearer_token + ''
        # define create mobile settlement account payload
        create_mobile_settlement_account_payload = json_builder.mobile_settlement_account(first_name=first_name,
                                                                                          last_name=last_name,
                                                                                          phone_number=phone_number,
                                                                                          network=network)
        return self._make_requests(headers=headers,
                                   method='POST',
                                   url=create_mobile_wallet_settlement_account_url,
                                   payload=create_mobile_settlement_account_payload)

    def settle_funds(self, kwargs):
        """
        Creates a transfer from merchant account to a different settlement account.
        Returns a request response object < class, 'requests.models.Response'>
        :param kwargs: The values constitute all user input.
        :type kwargs: dict
        :return: requests.models.Response
        """
        if 'access_token' not in kwargs:
            raise exceptions.InvalidArgumentError('Access Token not given.')
        else:
            bearer_token = kwargs['access_token']

        if 'currency' not in kwargs:
            currency = 'KES'
        if 'destination_reference' not in kwargs:
            destination_reference = ''
        if 'destination_type' not in kwargs:
            destination_type = ''

        if 'callback_url' not in kwargs:
            raise exceptions.InvalidArgumentError('Invalid arguments for creating Outgoing Pay.')

        # iterate through kwargs
        if 'callback_url' in kwargs:
            callback_url = kwargs['callback_url']
        if 'destination_type' in kwargs:
            destination_type = kwargs['destination_type']
        if 'destination_reference' in kwargs:
            destination_reference = kwargs['destination_reference']
        if 'value' in kwargs:
            value = kwargs['value']

        # build settle funds url
        settle_funds_url = self._build_url(TRANSFER_PATH)

        # define headers
        headers = dict(self._headers)

        # check bearer token
        validation.validate_string_arguments(bearer_token)

        # add authorization to headers
        headers['Authorization'] = 'Bearer ' + bearer_token + ''

        # define amount
        if 'value' in kwargs:
            validation.validate_string_arguments(currency, value)
            transfer_amount = json_builder.amount(currency=currency, value=value)

        # create links json object
        transfer_links = json_builder.links(callback_url=callback_url)

        if destination_reference == '' and destination_type == '':
            settle_funds_payload = json_builder.transfers(transfer_links=transfer_links)
        else:
            settle_funds_payload = json_builder.transfers(transfer_links=transfer_links,
                                                          transfers_amount=transfer_amount,
                                                          destination_type=destination_type,
                                                          destination_reference=destination_reference)
        return self._make_requests(headers=headers,
                                   method='POST',
                                   url=settle_funds_url,
                                   payload=settle_funds_payload)

    def transfer_transaction_status(self,
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
    def transfer_transaction_location(response):
        """
        Returns location of the transfers transaction result as returned in the headers of the
        response body.
        :param response: response object from a HTTP request
        :type response: requests.models.Response
        :return str
        """
        return service.k2_requests.get_location(response)
