"""
This module handles the k2-connect PAY service. It entails the creation
of payments and pay recipients within the pay service. Once a transaction
is created, the service provides the user with a means to query k2 servers
for the pay transaction's status.
"""
from k2connect import service, json_builder, exceptions, validation

# PAY Service paths
ADD_PAY_PATH = "api/v1/pay_recipients"
SEND_PAY_PATH = "api/v1/payments"

# PAY recipient types
BANK_ACCOUNT_RECIPIENT_TYPE = "bank_account"
MOBILE_WALLET_RECIPIENT_TYPE = "mobile_wallet"
TILL_RECIPIENT_TYPE = "till"
PAYBILL_RECIPIENT_TYPE = "paybill"


class PayService(service.Service):
    """
    The PayService class containing methods to:
    To create pay recipients
    Example:
        >>>import k2connect
        >>>k2connect.initialize('sample_client_id', 'sample_client_secret', 'https://some_url.com/')
        >>> pay = k2-connect.Pay
        >>> pay_recipient = pay.add_pay_recipient(recipient_type='mobile_wallet',
        >>>.......................................first_name='Jaqen',
        >>>.......................................last_name='Hghar',
        >>>.......................................phone='+007856798451',
        >>>.......................................network='Valyria Mobile')
    To send payments to third parties
    Example:
        >>> pay_transaction = pay.send_pay('https://mycoolapp.com',
        >>>................................'c7f300c0-f1ef-4151-9bbe-005005aa3747',
        >>>................................'25000',
        >>>................................customerId='8675309',
        >>>................................notes='Salary payment for May 2018')
    To check transaction statuses
    Example:
        >>> pay.transaction status(pay_transaction)
        '{"status":"Scheduled","reference":"KKKKKKKKK",
        "origination_time":"2018-07-20T22:45:12.790Z",
        "destination":"c7f300c0-f1ef-4151-9bbe-005005aa3747",
        "amount":{"currency":"KES","value":20000},"
        metadata":{"customerId":"8675309",
        "notes":"Salary payment for May 2018"},
        "_links":{"self":"https://api-sandbox.kopokopo.com/payments
        /d76265cd-0951-e511-80da-0aa34a9b2388"}}'
    get payment request location
    Example:object
        >>> pay.pay_transaction_location(pay_transaction)
        'https://api-sandbox.kopokopo.com/payments/c7f300c0-f1ef-4151-9bbe-005005aa3747'
    """

    def __init__(self, base_url):
        """
        :param base_url: The domain to use in the library.
        :type base_url: str
        """
        super(PayService, self).__init__(base_url=base_url)

    def add_pay_recipient(self, kwargs):
        """
        Adds external entities that will be the destination of your payments.
        Returns a request response object < class, 'requests.models.Response'>
        :param kwargs: The values constitute all user input.
        :type kwargs: dict
        :return:'requests.models.Response'
        """
        if 'access_token' not in kwargs:
            raise exceptions.InvalidArgumentError('Access Token not given.')
        else:
            bearer_token = kwargs['access_token']

        if 'recipient_type' not in kwargs:
            raise exceptions.InvalidArgumentError('Recipient Type not given.')
        else:
            recipient_type = kwargs['recipient_type']

        # define headers
        headers = dict(self._headers)

        validation.validate_string_arguments(bearer_token)

        # add bearer token
        headers['Authorization'] = 'Bearer ' + bearer_token

        # build url
        add_pay_url = self._build_url(url_path=ADD_PAY_PATH)

        if 'email' in kwargs:
            validation.validate_email(str(kwargs['email']))
        if 'phone_number' in kwargs:
            validation.validate_phone_number(str(kwargs['phone_number']))

        # expected parameters for bank account wallet recipient
        if recipient_type == BANK_ACCOUNT_RECIPIENT_TYPE:
            if 'account_name' not in kwargs or \
                    'account_number' not in kwargs or \
                    'settlement_method' not in kwargs or \
                    'bank_branch_ref' not in kwargs:
                raise exceptions.InvalidArgumentError('Invalid arguments for bank account Pay recipient')

            # build recipient json object
            recipient_object = json_builder.bank_account(account_name=str(kwargs['account_name']),
                                                         account_number=str(kwargs['account_number']),
                                                         settlement_method=str(kwargs['settlement_method']),
                                                         bank_branch_ref=str(kwargs['bank_branch_ref']))
            # build bank payment recipient json object
            payment_recipient_object = json_builder.pay_recipient(recipient_type=recipient_type,
                                                                  recipient=recipient_object)
        # expected parameters for mobile wallet recipient
        # ['first_name', 'last_name',
        # network','phone_number','email']

        elif recipient_type == MOBILE_WALLET_RECIPIENT_TYPE:
            if 'first_name' not in kwargs or \
                    'last_name' not in kwargs or \
                    'phone_number' not in kwargs or \
                    'email' not in kwargs or \
                    'network' not in kwargs:
                raise exceptions.InvalidArgumentError('Invalid arguments for mobile wallet Pay recipient')

            # create recipient json object
            recipient_object = json_builder.mobile_wallet(first_name=str(kwargs['first_name']),
                                                          last_name=str(kwargs['last_name']),
                                                          phone_number=str(kwargs['phone_number']),
                                                          network=str(kwargs['network']),
                                                          email=str(kwargs['email']))

            # create mobile wallet recipient json object
            payment_recipient_object = json_builder.pay_recipient(recipient_type=recipient_type,
                                                                  recipient=recipient_object)

        elif recipient_type == TILL_RECIPIENT_TYPE:
            if 'till_name' not in kwargs or \
                    'till_number' not in kwargs:
                raise exceptions.InvalidArgumentError('Invalid arguments for till Pay recipient')

            # create recipient json object
            recipient_object = json_builder.till_pay_recipient(till_name=str(kwargs['till_name']),
                                                          till_number=str(kwargs['till_number']))

            # create mobile wallet recipient json object
            payment_recipient_object = json_builder.pay_recipient(recipient_type=recipient_type,
                                                                  recipient=recipient_object)
        # expected parameters for mobile wallet recipient
        # ['till_name', 'till_number']

        elif recipient_type == PAYBILL_RECIPIENT_TYPE:
            if 'paybill_name' not in kwargs or \
                    'paybill_number' not in kwargs or \
                    'paybill_account_number' not in kwargs:
                raise exceptions.InvalidArgumentError('Invalid arguments for paybill Pay recipient')

            # create recipient json object
            recipient_object = json_builder.paybill_pay_recipient(paybill_name=str(kwargs['paybill_name']),
                                                                  paybill_number=str(kwargs['paybill_number']),
                                                                  paybill_account_number=str(kwargs['paybill_account_number']))

            # create mobile wallet recipient json object
            payment_recipient_object = json_builder.pay_recipient(recipient_type=recipient_type,
                                                                  recipient=recipient_object)
        # expected parameters for mobile wallet recipient
        # ['alias_name', 'till_number']

        else:
            raise exceptions.InvalidArgumentError('The recipient type is not recognized by k2connect')

        return self._make_requests(headers=headers,
                                   method='POST',
                                   url=add_pay_url,
                                   payload=payment_recipient_object)

    def send_pay(self, kwargs):
        """
        Creates an outgoing pay to a third party. The result of
        the pay is provided asynchronously and posted to the callback_url
        provided.
        Returns a request response object < class, 'requests.models.Response'>
        :param kwargs: Provision for optional metadata with maximum of 5
        key value pairs.
        :type kwargs: dict

        :return:requests.models.Response
        """
        if 'access_token' not in kwargs:
            raise exceptions.InvalidArgumentError('Access Token not given.')

        if 'destination_reference' not in kwargs or \
                'destination_type' not in kwargs or \
                'callback_url' not in kwargs or \
                'description' not in kwargs or \
                'amount' not in kwargs:
            raise exceptions.InvalidArgumentError('Invalid arguments for creating Outgoing Pay.')

        if 'currency' not in kwargs:
            currency = 'KES'

        if 'metadata' not in kwargs:
            pay_metadata = ''

        # iterate through kwargs
        if 'access_token' in kwargs:
            bearer_token = kwargs['access_token']
        if 'callback_url' in kwargs:
            callback_url = kwargs['callback_url']
        if 'description' in kwargs:
            description = kwargs['description']
        if 'currency' in kwargs:
            currency = 'KES'
        if 'metadata' in kwargs:
            pay_metadata = json_builder.metadata(kwargs['metadata'])

        # build send_pay url
        send_pay_url = self._build_url(SEND_PAY_PATH)

        # define headers
        headers = dict(self._headers)

        # check bearer token
        validation.validate_string_arguments(bearer_token)

        # add authorization to headers
        headers['Authorization'] = 'Bearer ' + bearer_token + ''

        # create amount json object
        pay_amount = json_builder.amount(currency=currency,
                                         value=kwargs['amount'])

        # create links json object
        pay_links = json_builder.links(callback_url=callback_url)

        # create payment json object
        pay_json = json_builder.pay(kwargs['destination_reference'],
                                    kwargs['destination_type'],
                                    pay_amount,
                                    description,
                                    pay_links,
                                    pay_metadata)

        return self._make_requests(url=send_pay_url,
                                   method='POST',
                                   payload=pay_json,
                                   headers=headers)

    def pay_transaction_status(self,
                               bearer_token,
                               query_url):
        """
        Returns a JSON object result containing the transaction status.
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
    def pay_transaction_location(response):
        """
        Returns location of the pay transaction result as returned in the headers of the
        response body.
        :param response: response object from a HTTP request
        :type response: requests.models.Response
        :return str
        """
        return service.k2_requests.get_location(response)
