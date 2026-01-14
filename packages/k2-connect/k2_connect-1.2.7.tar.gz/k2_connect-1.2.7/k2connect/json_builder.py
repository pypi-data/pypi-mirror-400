"""
This module handles the building of JSON objects for HTTPS requests
in the k2-connect library. It serializes python dictionaries to a JSON
formatted strings.
Example:
    >>>import json
    >>>sample_dict = {'key': 'value'}
    >>>print(json.dumps(sample_dict))
    "{"key": "value"}"
"""
import json
from k2connect import exceptions
from k2connect import validation


# serialize python dicts to JSON str
def serializer(dictionary):
    """
    Serializes python dict to json formatted str.
    Returns str.

    :param dictionary:
    :type dictionary: dict
    :return: str
    """
    validation.validate_dictionary_arguments(dictionary)
    return json.dumps(dictionary)


# special function
def metadata(join=None, **kwargs):
    """
    Returns a json formatted str with a maximum of 5 metadata key-value pairs.
    :param join:
    :param kwargs: Metadata information
    :return: str
    """
    if kwargs is None or kwargs == '':
        raise exceptions.InvalidArgumentError('Invalid argument passed. Expects ' / 'key=word/')
    if len(kwargs) >= 5:
        raise exceptions.InvalidArgumentError('Should be less than or 5 metadata objects')
    metadata_object = kwargs
    return metadata_object


def links(callback_url):
    """
    Validates url passed. Returns a str containing a callback_url.
    :param callback_url: Callback URL to post result.
    :type callback_url: str
    :return: str
    """
    # validate string argument
    validation.validate_string_arguments(callback_url)

    # validate url value
    validation.validate_url(callback_url)

    links_object = {'callback_url': callback_url}
    return links_object


def amount(currency, value):
    """
    Returns json formatted str containing currency and value.
    :param currency: Currency of amount
    :type currency: str
    :param value: Value of money
    :type value: str
    :return: str
    """
    # validate str arguments
    validation.validate_string_arguments(currency, value)

    amount_object = {'currency': currency, 'value': value}
    return amount_object


def bank_account(account_name,
                 account_number,
                 settlement_method,
                 bank_branch_ref,
                 **kwargs):
    """
    Returns a json formatted str with the optional value of email and phone.
    Checks if optional values are present, else passes values as null.
    :param account_name: Name as indicated on the bank account name.
    :type account_name: str
    :param account_number: Bank account number.
    :type account_number: str
    :param bank_branch_ref: Identifier identifying the destination bank branch.
    :type bank_branch_ref: str
    :param settlement_method: Whether bank account can settle via EFT or RTS
    :type settlement_method: str
    :param kwargs: Provision for optional 'email' and 'phone' information.
    :type kwargs: kwargs
    :return: str
    """
    # validate string arguments
    validation.validate_string_arguments(account_name,
                                         account_number,
                                         settlement_method,
                                         bank_branch_ref)

    bank_account_object = {'account_name': account_name,
                           'account_number': account_number,
                           'settlement_method': settlement_method,
                           'bank_branch_ref': bank_branch_ref}
    return bank_account_object


def bank_settlement_account(settlement_method,
                            account_name,
                            account_number,
                            bank_branch_ref):
    """
    Returns a json formatted str with bank settlement account information.
    :param settlement_method: EFT or RTS method to transfer funds
    :type settlement_method: str
    :param account_name: The name as indicated on the bank account name
    :type account_name: str
    :param account_number: The bank account number
    :type account_number: str
    :param bank_branch_ref: An identifier identifying the destination bank branch
    :type bank_branch_ref: str
    """
    # validate string arguments
    validation.validate_string_arguments(settlement_method,
                                         account_name,
                                         account_number,
                                         bank_branch_ref)

    bank_settlement_account_object = {'settlement_method': settlement_method,
                                      'account_name': account_name,
                                      'account_number': account_number,
                                      'bank_branch_ref': bank_branch_ref
                                      }
    return bank_settlement_account_object


def mobile_settlement_account(first_name,
                              last_name,
                              phone_number,
                              network):
    """
    Returns a json formatted str with bank settlement account information.
    :param first_name: First name of the recipient.
    :type first_name: str
    :param last_name: Last name of the recipient.
    :type last_name: str
    :param phone_number: The mobile phone number
    :type phone_number: str
    :param network: The bank account number
    :type network: str
    """
    # validate string arguments
    validation.validate_string_arguments(first_name,
                                         last_name,
                                         phone_number,
                                         network)

    mobile_settlement_account_object = {'first_name': first_name,
                                        'last_name': last_name,
                                        'phone_number': phone_number,
                                        'network': network
                                        }
    return mobile_settlement_account_object


def mobile_wallet(first_name,
                  last_name,
                  phone_number,
                  network,
                  **kwargs):
    """
    Returns a json formatted str with the optional value of email.
    Checks if optional value is present, else passes values as null.

    :param first_name: First name of the recipient.
    :type first_name: str
    :param last_name: Last name of the recipient.
    :type last_name: str
    :param phone_number: Phone number of recipient.
    :type phone_number: str
    :param network: The mobile network to which the phone number belongs.
    :type network: str
    :param kwargs: Provision for optional 'email' value
    :type kwargs: kwargs
    :return:
    """
    # validate string arguments
    validation.validate_string_arguments(first_name,
                                         last_name,
                                         phone_number,
                                         network)

    if 'email' not in kwargs:
        email = 'Null'
    else:
        email = kwargs['email']

    mobile_wallet_object = {'first_name': first_name,
                            'last_name': last_name,
                            'phone_number': phone_number,
                            'network': network,
                            'email': email
                            }
    return mobile_wallet_object


def pay_recipient(recipient_type, recipient):
    """
    Returns json formatted str containing pay recipient object.
    :param recipient_type: Type of recipient eg. mobile wallet
    or bank account
    :type recipient_type: str
    :param recipient: JSON formatted str containing details of the
    recipient
    :type recipient: str
    :return: str
    """
    # validate string arguments
    validation.validate_string_arguments(*recipient, recipient_type)

    recipient_object = {'type': recipient_type, 'pay_recipient': recipient}
    return recipient_object


def till_pay_recipient(till_name, till_number):
    """
    Returns a json formatted str with the optional value of email.
    Checks if optional value is present, else passes values as null.

    :param till_name: First name of the recipient.
    :type till_name: str
    :param till_number: Last name of the recipient.
    :type till_number: str
    :return:
    """
    # validate string arguments
    validation.validate_string_arguments(till_name,
                                         till_number)

    till_pay_recipient_object = {'till_name': till_name,
                                 'till_number': till_number
                                 }
    return till_pay_recipient_object


def paybill_pay_recipient(paybill_name, paybill_number, paybill_account_number):
    """
    Returns a json formatted str with the optional value of email.
    Checks if optional value is present, else passes values as null.

    :param paybill_name: Business name of the business.
    :type paybill_name: str
    :param paybill_number: Paybill business number.
    :type paybill_number: str
    :param paybill_account_number: Account number for the paybill.
    :type paybill_account_number: str
    :return:
    """
    # validate string arguments
    validation.validate_string_arguments(paybill_name, paybill_number, paybill_account_number)

    paybill_pay_recipient_object = {'paybill_name': paybill_name,
                                    'paybill_number': paybill_number,
                                    'paybill_account_number': paybill_account_number
                                    }
    return paybill_pay_recipient_object


def subscriber(first_name,
               last_name,
               phone_number,
               email,
               **kwargs):
    """
    Returns JSON formatted str containing subscriber information
    :param first_name: First name of the subscriber
    :type first_name: str
    :param last_name: Last name of the subscriber
    :type last_name: str
    :param phone_number: Phone number of the subscriber from which the
    pay will be made
    :type phone_number: str
    :param email: Email of the subscriber
    :type email: str
    :param kwargs: Provision for optional 'email' information.
    :type kwargs: str
    :return: str
    """
    # validate string arguments
    validation.validate_string_arguments(first_name,
                                         last_name,
                                         phone_number)
    if email != "Null":
        validation.validate_email(email)

    # if 'email' not in kwargs:
    #     email = 'Null'
    # else:
    #     email = kwargs['email']

    subscriber_object = {'first_name': first_name,
                         'last_name': last_name,
                         'phone_number': phone_number,
                         'email': email}

    return subscriber_object


def mpesa_payment(mpesa_links,
                  mpesa_payment_amount,
                  mpesa_payment_subscriber,
                  payment_channel,
                  till_number,
                  **kwargs):
    """
    Returns JSON formatted str with optional 'metadata' JSON str object.
    :param mpesa_links: A JSON object containing the call back URL
    :type mpesa_links: str
    :param payment_channel: Payment channel e.g MPESA
    :type payment_channel: str
    :param till_number: Till to which the pay is made.
    :type till_number: str
    :param mpesa_payment_subscriber: Subscriber JSON object.
    :type mpesa_payment_subscriber str
    :param mpesa_payment_amount: Amount JSON object.
    :type mpesa_payment_amount str
    :param kwargs: Optional JSON object containing a maximum of 5 key
    value pairs.
    :return: str
    """

    # validate string arguments
    validation.validate_string_arguments(*mpesa_links,
                                         *mpesa_payment_amount,
                                         *mpesa_payment_subscriber,
                                         *payment_channel,
                                         *till_number)

    if 'metadata' not in kwargs:
        mpesa_payment_metadata = {}
    else:
        mpesa_payment_metadata = kwargs['metadata']

    mpesa_payment_object = {'payment_channel': payment_channel,
                            'till_number': till_number,
                            'subscriber': mpesa_payment_subscriber,
                            'amount': mpesa_payment_amount,
                            'metadata': mpesa_payment_metadata,
                            '_links': mpesa_links
                            }

    return mpesa_payment_object


def webhook_subscription(event_type,
                         webhook_endpoint,
                         scope,
                         scope_reference=None):
    """
    Returns JSON formatted str containing webhook subscription information
    :param event_type:The type of event subscribed to.
    :type event_type:  str
    :param webhook_endpoint: The HTTP end point to send the webhook.
    :type webhook_endpoint: str
    :param scope: A string that will be used to specify whether account is at Till or Company level.
    :type scope: str
    :param scope_reference: A string that represents the account number (eg MPESA till number).
    :type scope_reference: str
    :return: str
    """

    # validate string arguments
    validation.validate_string_arguments(event_type,
                                         webhook_endpoint,
                                         scope)
    if scope_reference is not None:
        validation.validate_string_arguments(scope_reference)

    webhook_subscription_object = {'event_type': event_type,
                                   'url': webhook_endpoint,
                                   'scope': scope,
                                   'scope_reference': scope_reference
                                   }
    return webhook_subscription_object


def pay(destination_reference,
        destination_type,
        payment_amount,
        description,
        payment_links,
        payment_metadata):
    """
    Return JSON formatted str containing information about a transfer.
    :param destination_reference: reference for the pay_recipient account.
    :type destination_reference : str
    :param destination_type: Differentiate between mobile and bank account type for recipient
    :type destination_type : str
    :param payment_amount: A JSON formatted str containing the currency
    and the amount to be transferred.
    :type payment_amount: str
    :param description: Description or purpose of payment.
    :type description: str
    :param payment_metadata: A JSON formatted str with a maximum of 5
    key-value pairs.
    :type payment_metadata: str
    :param payment_links:A JSON formatted str containing a call back URL.
    :type payment_links: str
    :return: str
    """

    # validate string arguments
    validation.validate_string_arguments(*destination_reference,
                                         *destination_type,
                                         *payment_amount,
                                         *description,
                                         *payment_links,
                                         *payment_metadata)

    payment_json_object = {
        "destination_reference": destination_reference,
        "destination_type": destination_type,
        "amount": payment_amount,
        "description": description,
        "metadata": payment_metadata,
        "_links": payment_links
    }
    return payment_json_object


def transfers(transfer_links, **kwargs):
    """
    Returns JSON formatted containing information about a transfer.
    :param transfers_amount: Amount to be transferred.
    :type transfers_amount: str
    :param transfer_links: Links containing Callback URL.
    :type transfer_links: str
    :param kwargs: Provision for optional 'destination' value.
    :type kwargs: str
    :return: str
    """
    # validate string arguments
    if transfer_links is not None:
        validation.validate_string_arguments(*transfer_links)
    
    if 'transfers_amount' in kwargs:
        transfers_amount = kwargs['transfers_amount']
        validation.validate_string_arguments(*transfers_amount)
    else:
        transfers_amount = None

    if 'destination_type' not in kwargs:
        destination_type = None
    else:
        destination_type = kwargs['destination_type']

    if 'destination_reference' not in kwargs:
        destination_reference = None
    else:
        destination_reference = kwargs['destination_reference']

    transfers_object = {'amount': transfers_amount,
                        'destination_reference': destination_reference,
                        'destination_type': destination_type,
                        '_links': transfer_links
                        }
    return transfers_object


def transaction_sms_notification(webhook_event_reference, message, notification_links):
    """
    Returns JSON formatted containing information about a transfer.
    :param webhook_event_reference: Reference for webhook event.
    :type webhook_event_reference: str
    :param message: Message to be sent.
    :type message: str
    :param notification_links: Links containing callback URL.
    :type notification_links: str
    :return: str
    """
    # validate string arguments
    validation.validate_string_arguments(*webhook_event_reference, *message, *notification_links)

    transaction_sms_notification_object = {'webhook_event_reference': webhook_event_reference,
                                           'message': message,
                                           '_links': notification_links
                                           }
    return transaction_sms_notification_object


def polling(scope, scope_reference, from_time, to_time, polling_links):
    """
    Returns JSON formatted containing information about a transfer.
    :param scope: Amount to be transferred.
    :type scope: str
    :param scope_reference: Links containing Callback URL.
    :type scope_reference: str
    :param from_time: Defines the beginning start time.
    :type from_time: str
    :param to_time: Defines the beginning end time.
    :type to_time: str
    :param polling_links: Contains callback_url.
    :type polling_links: str
    :return: str
    """
    # validate string arguments
    validation.validate_string_arguments(*scope, *scope_reference, *from_time, *to_time, *polling_links)

    transfers_object = {'scope': scope,
                        'scope_reference': scope_reference,
                        'from_time': from_time,
                        'to_time': to_time,
                        '_links': polling_links
                        }
    return transfers_object
