"""
This module is responsible for the processing of payloads in k2-connect.
It converts JSON objects to python dictionaries then breaks down the python
dictionaries and sets their values to predefined "names" that correspond to
their respective keys in the JSON object using python properties.
:Example:
    sample_dictionary = {'key': 'value'}
    instance_of_payload_decomposer.key = sample_dictionary['value']
"""
import json
from k2connect import exceptions
from k2connect import k2_model
from k2connect import validation

B2B_TRANSACTION_RECEIVED = 'b2b_transaction_received'
BUYGOODS_TRANSACTION_RECEIVED = 'buygoods_transaction_received'
CREATE_PAYMENT = 'payment'
RECEIVE_PAYMENTS = 'incoming_payment'
TRANSFER = 'settlement_transfer'
# TODO: Pending
BUYGOODS_TRANSACTION_REVERSED = 'buygoods_transaction_reversed'
CUSTOMER_CREATED = 'customer_created'
MERCHANT_TO_MERCHANT_TRANSACTION_RECEIVED = 'm2m_transaction_received'
SETTLEMENT_TRANSFER_COMPLETED = 'settlement_transfer_completed'


def decompose(json_payload):
    """
    Returns an instance of the K2Model class. The decomposer object is used to
    set values that are then accessible through python properties of the same name
    as the setters.
    Example:
        For the JSON object:
        x = {
             "resource": {
                "sender_first_name": "Tyrion",
                "sender_last_name": "Lanister"
                }
            }


        >>>from k2connect import k2_model
        >>>decomposer = k2_model.K2Model()
        >>>resource_payload_nest = payload_dictionary['event']['resource']
        >>>decomposer.first_name = resource_payload_nest['sender_first_name']
        test
        >>> print(decomposer.first_name)
        'Tyrion'

    :param json_payload: A JSON formatted str object
    :type json_payload: str
    """
    validation.validate_string_arguments(*json_payload)

    # convert json object to python dictionary for decomposing
    payload_dictionary = json.loads(json_payload)

    # validate dictionary
    validation.validate_dictionary_arguments(payload_dictionary)

    # define decomposer
    decomposer = k2_model.K2Model()

    # Webhooks
    if 'data' not in payload_dictionary:
        result_topic = payload_dictionary['topic']
        decomposer.topic = result_topic
        webhook_event_nest = payload_dictionary['event']
        webhook_result_type = webhook_event_nest['type']
        resource_payload_nest = webhook_event_nest['resource']
        links_payload_nest = payload_dictionary['_links']
        decomposer.result_type = webhook_result_type
        webhook_decompose(decomposer, result_topic, payload_dictionary, resource_payload_nest, links_payload_nest)
    elif 'data' in payload_dictionary:
        # Payments
        data_payload_nest = payload_dictionary['data']
        payments_result_type = data_payload_nest['type']
        payments_attributes_payload_nest = data_payload_nest['attributes']
        payments_metadata_payload_nest = payments_attributes_payload_nest['metadata']
        payments_links_payload_nest = payments_attributes_payload_nest['_links']
        payment_decompose(decomposer, data_payload_nest, payments_result_type, payments_attributes_payload_nest,
                          payments_links_payload_nest)
        decomposer.metadata = payments_metadata_payload_nest
    return decomposer


def webhook_decompose(decomposer, result_topic, payload_dictionary, resource_payload_nest, links_payload_nest):
    # decompose ID values that are similar in ALL WEBHOOKS
    if result_topic == B2B_TRANSACTION_RECEIVED \
            or result_topic == BUYGOODS_TRANSACTION_RECEIVED \
            or result_topic == BUYGOODS_TRANSACTION_REVERSED \
            or result_topic == CUSTOMER_CREATED \
            or result_topic == MERCHANT_TO_MERCHANT_TRANSACTION_RECEIVED \
            or result_topic == SETTLEMENT_TRANSFER_COMPLETED:
        decomposer.id = payload_dictionary['id']
        decomposer.created_at = payload_dictionary['created_at']

    if result_topic == B2B_TRANSACTION_RECEIVED \
            or result_topic == BUYGOODS_TRANSACTION_RECEIVED \
            or result_topic == BUYGOODS_TRANSACTION_REVERSED \
            or result_topic == CUSTOMER_CREATED \
            or result_topic == MERCHANT_TO_MERCHANT_TRANSACTION_RECEIVED:
        decomposer.resourceId = resource_payload_nest['id']

    # decompose status value that are similar in TRANSACTIONS
    if result_topic == BUYGOODS_TRANSACTION_RECEIVED \
            or result_topic == B2B_TRANSACTION_RECEIVED \
            or result_topic == MERCHANT_TO_MERCHANT_TRANSACTION_RECEIVED \
            or result_topic == BUYGOODS_TRANSACTION_REVERSED \
            or result_topic == SETTLEMENT_TRANSFER_COMPLETED:
        decomposer.status = resource_payload_nest['status']
        decomposer.currency = resource_payload_nest['currency']
        decomposer.amount = resource_payload_nest['amount']
        decomposer.reference = resource_payload_nest['reference']
        decomposer.origination_time = resource_payload_nest['origination_time']

    # decompose system value that are similar in TRANSACTIONS
    if result_topic == BUYGOODS_TRANSACTION_RECEIVED \
            or result_topic == B2B_TRANSACTION_RECEIVED \
            or result_topic == BUYGOODS_TRANSACTION_REVERSED:
        decomposer.system = resource_payload_nest['system']
        decomposer.till_number = resource_payload_nest['till_number']

    # decompose all values that are similar in BUYGOODS TRANSACTIONS
    if result_topic == BUYGOODS_TRANSACTION_RECEIVED \
            or result_topic == BUYGOODS_TRANSACTION_REVERSED:
        decomposer.first_name = resource_payload_nest['sender_first_name']
        # decomposer.middle_name = resource_payload_nest['sender_middle_name']
        decomposer.last_name = resource_payload_nest['sender_last_name']

    # decompose all values that have similar links structures
    if result_topic == BUYGOODS_TRANSACTION_REVERSED \
            or result_topic == BUYGOODS_TRANSACTION_RECEIVED \
            or result_topic == SETTLEMENT_TRANSFER_COMPLETED \
            or result_topic == CUSTOMER_CREATED \
            or result_topic == B2B_TRANSACTION_RECEIVED \
            or result_topic == MERCHANT_TO_MERCHANT_TRANSACTION_RECEIVED:
        decomposer.links_self = links_payload_nest['self']
        decomposer.links_resource = links_payload_nest['resource']

        # decompose value specific to buygoods transaction reversed
        if result_topic == BUYGOODS_TRANSACTION_REVERSED:
            decomposer.reversal_time = resource_payload_nest['reversal_time']

    # decompose unique to b2b transaction received
    if result_topic == B2B_TRANSACTION_RECEIVED:
        decomposer.sending_till = resource_payload_nest['sending_till']
        decomposer.till_number = resource_payload_nest['till_number']

    # decompose unique to merchant to merchant transaction received
    if result_topic == MERCHANT_TO_MERCHANT_TRANSACTION_RECEIVED:
        decomposer.sending_merchant = resource_payload_nest['sending_merchant']

    # decompose unique to customer created
    if result_topic == CUSTOMER_CREATED:
        decomposer.first_name = resource_payload_nest['first_name']
        decomposer.middle_name = resource_payload_nest['middle_name']
        decomposer.last_name = resource_payload_nest['last_name']

    # decompose unique to settlement transfer completed
    if result_topic == SETTLEMENT_TRANSFER_COMPLETED:
        destination_payload_nest = resource_payload_nest['destination']
        decomposer.destination_type = destination_payload_nest['type']
        destination_resource_payload_nest = destination_payload_nest['resource']
        if decomposer.destination_type == 'merchant_bank_account':
            decomposer.bank_id = destination_resource_payload_nest['bank_id']
            decomposer.bank_branch_id = destination_resource_payload_nest['bank_branch_id']
            decomposer.account_name = destination_resource_payload_nest['account_name']
            decomposer.account_number = destination_resource_payload_nest['account_number']
        elif decomposer.destination_type == 'merchant_wallet':
            decomposer.msisdn = destination_resource_payload_nest['msisdn']
            decomposer.network = destination_resource_payload_nest['network']


def payment_decompose(decomposer, data_payload_nest, payments_result_type, payments_attributes_payload_nest,
                      payments_links_payload_nest):
    # decompose all values that are common to PAYMENTS(OUTGOING OR INCOMING) and Transfer
    if payments_result_type == RECEIVE_PAYMENTS \
            or payments_result_type == CREATE_PAYMENT \
            or payments_result_type == TRANSFER:
        decomposer.id = data_payload_nest['id']
        decomposer.type = payments_result_type
        decomposer.status = payments_attributes_payload_nest['status']
        decomposer.self = payments_links_payload_nest['self']
        decomposer.callback_url = payments_links_payload_nest['callback_url']

    # decompose all values that are common to receive MPESA payments service (INCOMING)
    if payments_result_type == RECEIVE_PAYMENTS:
        decomposer.initiation_time = payments_attributes_payload_nest['initiation_time']
        # Event Payload
        payments_events_payload_nest = payments_attributes_payload_nest['event']
        decomposer.errors = payments_events_payload_nest['errors']
        decomposer.event_type = payments_events_payload_nest['type']
        # incoming payments resource payload
        payments_resource_payload_nest = payments_events_payload_nest['resource']
        decomposer.resource_id = payments_resource_payload_nest['id']
        decomposer.transaction_reference = payments_resource_payload_nest['reference']
        decomposer.origination_time = payments_resource_payload_nest['origination_time']
        decomposer.sender_phone_number = payments_resource_payload_nest['sender_phone_number']
        decomposer.amount = payments_resource_payload_nest['amount']
        decomposer.currency = payments_resource_payload_nest['currency']
        decomposer.till_number = payments_resource_payload_nest['till_number']
        decomposer.system = payments_resource_payload_nest['system']
        decomposer.resource_status = payments_resource_payload_nest['status']
        decomposer.sender_last_name = payments_resource_payload_nest['sender_last_name']
        decomposer.sender_first_name = payments_resource_payload_nest['sender_first_name']
        decomposer.sender_middle_name = payments_resource_payload_nest['sender_middle_name']

    # decompose all values that are common to the PAY (OUTGOING PAYMENTS) and TRANSFER service
    if payments_result_type == CREATE_PAYMENT \
            or payments_result_type == TRANSFER:
        decomposer.created_at = payments_attributes_payload_nest['created_at']
        decomposer.origination_time = payments_attributes_payload_nest['origination_time']
        decomposer.amount = payments_attributes_payload_nest['amount']['value']
        decomposer.currency = payments_attributes_payload_nest['amount']['currency']
        decomposer.transfer_batches = payments_attributes_payload_nest['transfer_batches']

    # decompose all values that are in the PAY service (OUTGOING PAYMENTS)
    if payments_result_type == CREATE_PAYMENT:
        decomposer.metadata = payments_attributes_payload_nest['metadata']
