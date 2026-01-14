"""
This module handles the creation of setters and python properties
for attributes. These methods set values from decomposed result payloads to
enable access to values in the result JSON payloads.
"""
from k2connect.attribute import attribute


class K2Model:
    """
    The Model class for creating setters and properties based on the
    attributes of different JSON objects
    """

    # attribute(
    #     # create properties and setters for JSON payload generic variables
    #     first_name=None,
    #     middle_name=None,
    #     last_name=None,
    #     amount=None,
    #     currency=None,
    #     status=None,
    #     reference=None,
    #     origination_time=None,
    #     msisdn=None,
    #     # create properties and setters for JSON payloads with errors"
    #     error_code=None,
    #     error_description=None,
    #     # create properties and setters for JSON payloads with links
    #     links_resource=None,
    #     links_self=None,
    #     payment_request=None,
    #     # create properties and setters for PAY JSON payloads
    #     destination=None,
    #     # create properties and setters for JSON payload in Receive MPESA service
    #     payment_result_status=None,
    #     payment_result_id=None,
    #     # create properties and setters for Settlement service JSON payloads
    #     transfer_time=None,
    #     transfer_type=None,
    #     destination_type=None,
    #     transfer_mode=None,
    #     bank=None,
    #     branch=None,
    #     account_number=None,
    #     # properties and setters for b2b transaction
    #     sending_till=None,
    #     # properties and setters for Merchant to Merchant transaction
    #     sending_merchant=None)
