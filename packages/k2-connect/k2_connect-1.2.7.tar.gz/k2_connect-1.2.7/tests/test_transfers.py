import requests
import unittest
from urlvalidator import URLValidator
from k2connect import transfers, authorization, json_builder, exceptions, validation
from k2connect.exceptions import InvalidArgumentError
from tests import SAMPLE_BASE_URL, SAMPLE_CLIENT_ID, SAMPLE_CLIENT_SECRET


class TransferTestCase(unittest.TestCase):
    verified_settlement_url = ''
    transfer_funds_url = ''
    # Establish environment
    validate = URLValidator()

    token_service = authorization.TokenService(SAMPLE_BASE_URL, SAMPLE_CLIENT_ID, SAMPLE_CLIENT_SECRET)
    access_token_request = token_service.request_access_token()
    ACCESS_TOKEN = token_service.get_access_token(access_token_request)

    settlement_transfer_obj = transfers.TransferService(base_url=SAMPLE_BASE_URL)
    header = dict(settlement_transfer_obj._headers)
    header['Authorization'] = 'Bearer ' + ACCESS_TOKEN

    def test_init_method_with_base_url_argument_succeeds(self):
        transfer_service = transfers.TransferService(base_url=SAMPLE_BASE_URL)
        self.assertIsInstance(transfer_service, transfers.TransferService)

    def test_init_method_without_base_url_argument_fails(self):
        self.assertRaises(TypeError, lambda: transfers.TransferService())

    # Add Settlement Accounts
    # Bank account
    def test_add_bank_settlement_account_for_RTS_transfer_succeeds(self):
        test_payload = {
            "access_token": TransferTestCase.ACCESS_TOKEN,
            "settlement_method": 'RTS',
            "account_name": 'py_sdk_account_name',
            "account_number": '12345678901234567890',
            "bank_branch_ref": '633aa26c-7b7c-4091-ae28-96c0687cf886'
        }
        self.assertIsNotNone(
            TransferTestCase.settlement_transfer_obj.add_bank_settlement_account(test_payload))

    def test_add_bank_settlement_account_for_EFT_transfer_succeeds(self):
        test_payload = {
            "access_token": TransferTestCase.ACCESS_TOKEN,
            "settlement_method": 'EFT',
            "account_name": 'py_sdk_account_name',
            "account_number": '12345678901234567890',
            "bank_branch_ref": '633aa26c-7b7c-4091-ae28-96c0687cf886'
        }
        self.assertIsNotNone(
            TransferTestCase.settlement_transfer_obj.add_bank_settlement_account(test_payload))

    def test_successful_add_bank_settlement_account_for_EFT_transfer_returns_resource_url(self):
        test_payload = {
            "access_token": TransferTestCase.ACCESS_TOKEN,
            "settlement_method": 'EFT',
            "account_name": 'py_sdk_account_name',
            "account_number": '12345678901234567890',
            "bank_branch_ref": '633aa26c-7b7c-4091-ae28-96c0687cf886'
        }
        response = TransferTestCase.settlement_transfer_obj.add_bank_settlement_account(test_payload)
        if self.assertIsNone(TransferTestCase.validate(response)) is None:
            TransferTestCase.verified_settlement_url = response
        self.assertIsNone(TransferTestCase.validate(response))

    def test_successful_add_bank_settlement_account_for_RTS_transfer_returns_resource_url(self):
        test_payload = {
            "access_token": TransferTestCase.ACCESS_TOKEN,
            "settlement_method": 'RTS',
            "account_name": 'py_sdk_account_name',
            "account_number": '12345678901234567890',
            "bank_branch_ref": '633aa26c-7b7c-4091-ae28-96c0687cf886'
        }
        response = TransferTestCase.settlement_transfer_obj.add_bank_settlement_account(test_payload)
        if self.assertIsNone(TransferTestCase.validate(response)) is None:
            TransferTestCase.verified_settlement_url = response
        self.assertIsNone(TransferTestCase.validate(response))

    def test_add_bank_settlement_account_for_EFT_transfer_request(self):
        response = requests.post(
            headers=TransferTestCase.header,
            json=json_builder.bank_settlement_account("EFT", "py_sdk_account_name", "12345678901234567890",
                                                      "633aa26c-7b7c-4091-ae28-96c0687cf886"),
            data=None,
            url=TransferTestCase.settlement_transfer_obj._build_url(transfers.SETTLEMENT_BANK_ACCOUNTS_PATH))
        self.assertEqual(response.status_code, 201)

    def test_add_bank_settlement_account_for_RTS_transfer_request(self):
        response = requests.post(
            headers=TransferTestCase.header,
            json=json_builder.bank_settlement_account("RTS", "py_sdk_account_name", "12345678901234567890",
                                                      "633aa26c-7b7c-4091-ae28-96c0687cf886"),
            data=None,
            url=TransferTestCase.settlement_transfer_obj._build_url(transfers.SETTLEMENT_BANK_ACCOUNTS_PATH))
        self.assertEqual(response.status_code, 201)

    # Failure scenarios
    def test_add_bank_settlement_account_with_invalid_params_fails(self):
        test_payload = {
            "access_token": TransferTestCase.ACCESS_TOKEN,
            "settlement_method": 'EFT',
            "account_number": 'account_number',
            "bank_branch_ref": '633aa26c-7b7c-4091-ae28-96c0687cf886'
        }
        with self.assertRaisesRegex(InvalidArgumentError, 'Invalid arguments for creating Bank Settlement Account.'):
            TransferTestCase.settlement_transfer_obj.add_bank_settlement_account(test_payload)

    # Mobile Wallet
    def test_add_mobile_wallet_settlement_account_succeeds(self):
        test_payload = {
            "access_token": TransferTestCase.ACCESS_TOKEN,
            "first_name": 'py_sdk_first_name',
            "last_name": 'py_sdk_last_name',
            "phone_number": '+254911222538',
            "network": 'Safaricom'
        }
        self.assertIsNotNone(
            TransferTestCase.settlement_transfer_obj.add_mobile_wallet_settlement_account(test_payload))

    def test_successful_add_mobile_wallet_settlement_account_returns_resource_url(self):
        test_payload = {
            "access_token": TransferTestCase.ACCESS_TOKEN,
            "first_name": 'py_sdk_first_name',
            "last_name": 'py_sdk_last_name',
            "phone_number": '+254911222538',
            "network": 'Safaricom'
        }
        response = TransferTestCase.settlement_transfer_obj.add_mobile_wallet_settlement_account(test_payload)
        if self.assertIsNone(TransferTestCase.validate(response)) is None:
            TransferTestCase.verified_settlement_url = response
        self.assertIsNone(TransferTestCase.validate(response))

    def test_add_mobile_wallet_settlement_account_request(self):
        response = requests.post(
            headers=TransferTestCase.header,
            json=json_builder.mobile_settlement_account("py_sdk_first_name", "py_sdk_last_name", "254900112502",
                                                        "safaricom"),
            data=None,
            url=TransferTestCase.settlement_transfer_obj._build_url(transfers.SETTLEMENT_MOBILE_ACCOUNTS_PATH))
        self.assertEqual(response.status_code, 201)

    # Failure scenarios
    def test_add_mobile_wallet_settlement_account_with_invalid_phone_fails(self):
        test_payload = {
            "access_token": TransferTestCase.ACCESS_TOKEN,
            "first_name": 'py_sdk_first_name',
            "last_name": 'py_sdk_last_name',
            "phone_number": 'phone_number',
            "network": 'Safaricom'
        }
        with self.assertRaises(InvalidArgumentError):
            TransferTestCase.settlement_transfer_obj.add_mobile_wallet_settlement_account(test_payload)

    # Transfer/Settle funds
    # Blind Transfer
    def test_blind_transfer_succeeds(self):
        test_payload = {
            "access_token": TransferTestCase.ACCESS_TOKEN,
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
        }
        self.assertIsNotNone(
            TransferTestCase.settlement_transfer_obj.settle_funds(test_payload))

    def test_successful_blind_transfer_transaction_returns_resource_url(self):
        test_payload = {
            "access_token": TransferTestCase.ACCESS_TOKEN,
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
        }
        response = TransferTestCase.settlement_transfer_obj.settle_funds(test_payload)
        if self.assertIsNone(TransferTestCase.validate(response)) is None:
            TransferTestCase.transfer_funds_url = response
        self.assertIsNone(TransferTestCase.validate(response))

    def test_successful_blind_transfer_request(self):
        response = requests.post(
            headers=TransferTestCase.header,
            json=json_builder.transfers(json_builder.links('https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d')),
            data=None,
            url=TransferTestCase.settlement_transfer_obj._build_url(transfers.TRANSFER_PATH))
        self.assertEqual(response.status_code, 201)

    # Targeted Transfer
    # Merchant Bank Account
    def test_targeted_transfer_to_merchant_bank_account_succeeds(self):
        test_payload = {
            "access_token": TransferTestCase.ACCESS_TOKEN,
            "destination_type": 'merchant_bank_account',
            "destination_reference": '87bbfdcf-fb59-4d8e-b039-b85b97015a7e',
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "value": '10',
        }
        self.assertIsNotNone(
            TransferTestCase.settlement_transfer_obj.settle_funds(test_payload))

    def test_successful_targeted_transfer_to_merchant_bank_account_returns_resource_url(self):
        test_payload = {
            "access_token": TransferTestCase.ACCESS_TOKEN,
            "destination_type": 'merchant_bank_account',
            "destination_reference": '87bbfdcf-fb59-4d8e-b039-b85b97015a7e',
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "value": '10',
        }
        response = TransferTestCase.settlement_transfer_obj.settle_funds(test_payload)
        if self.assertIsNone(TransferTestCase.validate(response)) is None:
            TransferTestCase.transfer_funds_url = response
        self.assertIsNone(TransferTestCase.validate(response))

    def test_successful_targeted_transfer_to_merchant_bank_account_request(self):
        response = requests.post(
            headers=TransferTestCase.header,
            json=json_builder.transfers(json_builder.links('https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d'),
                                        **{"transfers_amount": json_builder.amount('KES', "3300"),
                                           "destination_type": "merchant_bank_account",
                                           "destination_reference": "87bbfdcf-fb59-4d8e-b039-b85b97015a7e"}),
            data=None,
            url=TransferTestCase.settlement_transfer_obj._build_url(transfers.TRANSFER_PATH))
        self.assertEqual(response.status_code, 201)

    # Merchant Wallet
    def test_targeted_transfer_to_merchant_wallet_succeeds(self):
        test_payload = {
            "access_token": TransferTestCase.ACCESS_TOKEN,
            "destination_type": 'merchant_wallet',
            "destination_reference": 'eba238ae-e03f-46f6-aed5-db357fb00f9c',
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "value": '10',
        }
        self.assertIsNotNone(
            TransferTestCase.settlement_transfer_obj.settle_funds(test_payload))

    def test_successful_targeted_transfer_to_merchant_wallet_returns_resource_url(self):
        test_payload = {
            "access_token": TransferTestCase.ACCESS_TOKEN,
            "destination_type": 'merchant_wallet',
            "destination_reference": 'eba238ae-e03f-46f6-aed5-db357fb00f9c',
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "value": '10',
        }
        response = TransferTestCase.settlement_transfer_obj.settle_funds(test_payload)
        if self.assertIsNone(TransferTestCase.validate(response)) is None:
            TransferTestCase.transfer_funds_url = response
        self.assertIsNone(TransferTestCase.validate(response))

    def test_successful_targeted_transfer_to_merchant_wallet_request(self):
        response = requests.post(
            headers=TransferTestCase.header,
            json=json_builder.transfers(json_builder.links('https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d'),
                                        **{"transfers_amount": json_builder.amount('KES', "3300"),
                                           "destination_type": "merchant_wallet",
                                           "destination_reference": "eba238ae-e03f-46f6-aed5-db357fb00f9c"}),
            data=None,
            url=TransferTestCase.settlement_transfer_obj._build_url(transfers.TRANSFER_PATH))
        self.assertEqual(response.status_code, 201)

    # Query Transactions
    # Verified Settlement Account Status
    def test_successfully_added_settlement_account_status_succeeds(self):
        self.assertIsNotNone(
            TransferTestCase.settlement_transfer_obj.transfer_transaction_status(
                TransferTestCase.ACCESS_TOKEN,
                TransferTestCase.verified_settlement_url))

    def test_successfully_added_settlement_account_status_request(self):
        response = requests.get(
            headers=TransferTestCase.header,
            url=TransferTestCase.verified_settlement_url)
        self.assertEqual(response.status_code, 200)

    # Transfer Transaction Status
    def test_successful_transferred_funds_transaction_status_succeeds(self):
        self.assertIsNotNone(
            TransferTestCase.settlement_transfer_obj.transfer_transaction_status(
                TransferTestCase.ACCESS_TOKEN,
                TransferTestCase.transfer_funds_url))

    def test_successful_transferred_funds_transaction_status_request(self):
        response = requests.get(
            headers=TransferTestCase.header,
            url=TransferTestCase.transfer_funds_url)
        self.assertEqual(response.status_code, 200)

    # Failure scenarios
