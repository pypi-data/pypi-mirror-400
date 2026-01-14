import requests
import unittest
from urlvalidator import URLValidator
from k2connect import pay, exceptions, validation, authorization, json_builder
from k2connect.exceptions import InvalidArgumentError
from tests import SAMPLE_BASE_URL, SAMPLE_CLIENT_ID, SAMPLE_CLIENT_SECRET, PAY, MSG


class PayTestCase(unittest.TestCase):
    pay_transaction_query_url = ''
    pay_recipient_query_url = ''
    # Establish environment
    validate = URLValidator()

    token_service = authorization.TokenService(SAMPLE_BASE_URL, SAMPLE_CLIENT_ID, SAMPLE_CLIENT_SECRET)
    access_token_request = token_service.request_access_token()
    ACCESS_TOKEN = token_service.get_access_token(access_token_request)

    pay_obj = pay.PayService(base_url=SAMPLE_BASE_URL)
    header = dict(pay_obj._headers)
    header['Authorization'] = 'Bearer ' + ACCESS_TOKEN

    def test_init_method_with_base_url_argument_succeeds(self):
        pay_service = pay.PayService(base_url=SAMPLE_BASE_URL)
        self.assertIsInstance(pay_service, pay.PayService)

    def test_init_method_without_base_url_argument_fails(self):
        self.assertRaises(TypeError, lambda: pay.PayService())

    # Mobile Pay recipient
    def test_add_mobile_pay_recipient_succeeds(self):
        payload = PAY["mobile_pay"]
        payload.update({"access_token": PayTestCase.ACCESS_TOKEN, "recipient_type": 'mobile_wallet'})
        self.assertIsNotNone(
            PayTestCase.pay_obj.add_pay_recipient(payload))

    def test_successful_add_mobile_pay_receipient_request(self):
        response = requests.post(
            headers=PayTestCase.header,
            json=json_builder.pay_recipient("mobile_wallet",
                                            json_builder.mobile_wallet("first_name", "last_name", "9764ef5f-fcd6-42c1-bbff-de280becc64b",
                                                                       "safaricom")),
            data=None,
            url=PayTestCase.pay_obj._build_url(pay.ADD_PAY_PATH))
        self.assertEqual(response.status_code, 201)

    def test_add_mobile_pay_recipient_returns_resource_url(self):
        payload = PAY["mobile_pay"]
        payload.update({"access_token": PayTestCase.ACCESS_TOKEN, "recipient_type": 'mobile_wallet'})
        response = PayTestCase.pay_obj.add_pay_recipient(payload)
        if self.assertIsNone(PayTestCase.validate(response)) is None:
            PayTestCase.pay_recipient_query_url = response
        self.assertIsNone(PayTestCase.validate(response))

    # Mobile Pay Recipient Failure Scenarios
    def test_add_mobile_pay_recipient_nil_access_token_fails(self):
        with self.assertRaisesRegex(InvalidArgumentError, 'Access Token not given.'):
            PayTestCase.pay_obj.add_pay_recipient(PAY["mobile_pay"])

    def test_add_mobile_pay_recipient_nil_recipient_type_fails(self):
        with self.assertRaisesRegex(InvalidArgumentError, 'Access Token not given.'):
            PayTestCase.pay_obj.add_pay_recipient(PAY["mobile_pay"])

    def test_add_mobile_pay_recipient_without_first_name_fails(self):
        payload = PAY["invalid_first_name_mobile_pay"]
        payload.update({"access_token": PayTestCase.ACCESS_TOKEN, "recipient_type": 'mobile_wallet'})
        with self.assertRaises(InvalidArgumentError):
            PayTestCase.pay_obj.add_pay_recipient(payload)

    def test_add_mobile_pay_recipient_with_invalid_email_fails(self):
        payload = PAY["invalid_email_mobile_pay"]
        payload.update({"access_token": PayTestCase.ACCESS_TOKEN, "recipient_type": 'mobile_wallet'})
        with self.assertRaisesRegex(InvalidArgumentError, MSG["invalid_email"]):
            PayTestCase.pay_obj.add_pay_recipient(payload)

    def test_add_mobile_pay_recipient_with_invalid_phone_fails(self):
        payload = PAY["invalid_phone_mobile_pay"]
        payload.update({"access_token": PayTestCase.ACCESS_TOKEN, "recipient_type": 'mobile_wallet'})
        with self.assertRaisesRegex(InvalidArgumentError, MSG["invalid_phone"]):
            PayTestCase.pay_obj.add_pay_recipient(payload)

    # Bank Pay recipient
    def test_add_bank_pay_recipient_succeeds(self):
        payload = PAY["bank_pay"]
        payload.update({"access_token": PayTestCase.ACCESS_TOKEN, "recipient_type": 'bank_account'})
        self.assertIsNotNone(PayTestCase.pay_obj.add_pay_recipient(payload))

    def test_successful_add_bank_receipient_request(self):
        response = requests.post(
            headers=PayTestCase.header,
            json=json_builder.pay_recipient("bank_account",
                                            json_builder.bank_account(account_name="David Kariuki Python", account_number="566566", settlement_method="EFT",
                                                                      bank_branch_ref="633aa26c-7b7c-4091-ae28-96c0687cf886", )),
            data=None,
            url=PayTestCase.pay_obj._build_url(pay.ADD_PAY_PATH))
        self.assertEqual(response.status_code, 201)

    def test_add_bank_pay_recipient_returns_resource_url(self):
        payload = PAY["bank_pay"]
        payload.update({"access_token": PayTestCase.ACCESS_TOKEN, "recipient_type": 'bank_account'})
        response = PayTestCase.pay_obj.add_pay_recipient(payload)
        if self.assertIsNone(PayTestCase.validate(response)) is None:
            PayTestCase.pay_recipient_query_url = response
        self.assertIsNone(PayTestCase.validate(response))

    # Bank Pay Recipient Failure Scenarios
    def test_add_bank_pay_recipient_nil_access_token_fails(self):
        with self.assertRaisesRegex(InvalidArgumentError, 'Access Token not given.'):
            PayTestCase.pay_obj.add_pay_recipient(PAY["bank_pay"])

    def test_add_bank_pay_recipient_nil_recipient_type_fails(self):
        with self.assertRaisesRegex(InvalidArgumentError, 'Access Token not given.'):
            PayTestCase.pay_obj.add_pay_recipient(PAY["bank_pay"])

    def test_add_bank_pay_recipient_without_first_name_fails(self):
        payload = PAY["invalid_first_name_bank_pay"]
        payload.update({"access_token": PayTestCase.ACCESS_TOKEN, "recipient_type": 'bank_account'})
        with self.assertRaises(InvalidArgumentError):
            PayTestCase.pay_obj.add_pay_recipient(payload)

    def test_add_bank_pay_recipient_with_invalid_email_fails(self):
        payload = PAY["invalid_email_bank_pay"]
        payload.update({"access_token": PayTestCase.ACCESS_TOKEN, "recipient_type": 'bank_account'})
        with self.assertRaisesRegex(InvalidArgumentError, MSG["invalid_email"]):
            PayTestCase.pay_obj.add_pay_recipient(payload)

    def test_add_bank_pay_recipient_with_invalid_phone_fails(self):
        payload = PAY["invalid_phone_bank_pay"]
        payload.update({"access_token": PayTestCase.ACCESS_TOKEN, "recipient_type": 'bank_account'})
        with self.assertRaisesRegex(InvalidArgumentError, MSG["invalid_phone"]):
            PayTestCase.pay_obj.add_pay_recipient(payload)

    # Till Pay recipient
    def test_add_till_pay_recipient_succeeds(self):
        payload = PAY["till_pay"]
        payload.update({"access_token": PayTestCase.ACCESS_TOKEN, "recipient_type": 'till'})
        self.assertIsNotNone(PayTestCase.pay_obj.add_pay_recipient(payload))

    def test_successful_add_till_receipient_request(self):
        response = requests.post(
            headers=PayTestCase.header,
            json=json_builder.pay_recipient("till", json_builder.till_pay_recipient(till_name="Python Test Till", till_number="567567")),
            data=None,
            url=PayTestCase.pay_obj._build_url(pay.ADD_PAY_PATH))
        self.assertEqual(response.status_code, 201)

    def test_add_till_pay_recipient_returns_resource_url(self):
        payload = PAY["till_pay"]
        payload.update({"access_token": PayTestCase.ACCESS_TOKEN, "recipient_type": 'till'})
        response = PayTestCase.pay_obj.add_pay_recipient(payload)
        if self.assertIsNone(PayTestCase.validate(response)) is None:
            PayTestCase.pay_recipient_query_url = response
        self.assertIsNone(PayTestCase.validate(response))

    # Till Pay Recipient Failure Scenarios
    def test_add_till_pay_recipient_nil_access_token_fails(self):
        with self.assertRaisesRegex(InvalidArgumentError, 'Access Token not given.'):
            PayTestCase.pay_obj.add_pay_recipient(PAY["till_pay"])

    def test_add_till_pay_recipient_nil_recipient_type_fails(self):
        with self.assertRaisesRegex(InvalidArgumentError, 'Access Token not given.'):
            PayTestCase.pay_obj.add_pay_recipient(PAY["till_pay"])

    def test_add_till_pay_recipient_without_till_name_fails(self):
        payload = PAY["invalid_till_name_till_pay"]
        payload.update({"access_token": PayTestCase.ACCESS_TOKEN, "recipient_type": 'till'})
        with self.assertRaisesRegex(InvalidArgumentError, "Invalid arguments for till Pay recipient"):
            PayTestCase.pay_obj.add_pay_recipient(payload)

    def test_add_till_pay_recipient_without_till_number_fails(self):
        payload = PAY["invalid_till_number_till_pay"]
        payload.update({"access_token": PayTestCase.ACCESS_TOKEN, "recipient_type": 'till'})
        with self.assertRaisesRegex(InvalidArgumentError, "Invalid arguments for till Pay recipient"):
            PayTestCase.pay_obj.add_pay_recipient(payload)

    # Paybill Pay recipient
    def test_add_paybill_pay_recipient_succeeds(self):
        payload = PAY["paybill_pay"]
        payload.update({"access_token": PayTestCase.ACCESS_TOKEN, "recipient_type": 'paybill'})
        self.assertIsNotNone(PayTestCase.pay_obj.add_pay_recipient(payload))

    def test_successful_add_paybill_receipient_request(self):
        response = requests.post(
            headers=PayTestCase.header,
            json=json_builder.pay_recipient("paybill",
                                            json_builder.paybill_pay_recipient(paybill_name="Python Paybill", paybill_number="561830", paybill_account_number="account_two",)),
            data=None,
            url=PayTestCase.pay_obj._build_url(pay.ADD_PAY_PATH))
        self.assertEqual(response.status_code, 201)

    def test_add_paybill_pay_recipient_returns_resource_url(self):
        payload = PAY["paybill_pay"]
        payload.update({"access_token": PayTestCase.ACCESS_TOKEN, "recipient_type": 'paybill'})
        response = PayTestCase.pay_obj.add_pay_recipient(payload)
        if self.assertIsNone(PayTestCase.validate(response)) is None:
            PayTestCase.pay_recipient_query_url = response
        self.assertIsNone(PayTestCase.validate(response))

    # Paybill Pay Recipient Failure Scenarios
    def test_add_paybill_pay_recipient_nil_access_token_fails(self):
        with self.assertRaisesRegex(InvalidArgumentError, 'Access Token not given.'):
            PayTestCase.pay_obj.add_pay_recipient(PAY["paybill_pay"])

    def test_add_paybill_pay_recipient_nil_recipient_type_fails(self):
        with self.assertRaisesRegex(InvalidArgumentError, 'Access Token not given.'):
            PayTestCase.pay_obj.add_pay_recipient(PAY["paybill_pay"])

    def test_add_paybill_pay_recipient_without_paybill_name_fails(self):
        payload = PAY["invalid_paybill_name_paybill"]
        payload.update({"access_token": PayTestCase.ACCESS_TOKEN, "recipient_type": 'paybill'})
        with self.assertRaisesRegex(InvalidArgumentError, "Invalid arguments for paybill Pay recipient"):
            PayTestCase.pay_obj.add_pay_recipient(payload)

    def test_add_paybill_pay_recipient_without_paybill_number_fails(self):
        payload = PAY["invalid_paybill_number_paybill"]
        payload.update({"access_token": PayTestCase.ACCESS_TOKEN, "recipient_type": 'paybill'})
        with self.assertRaisesRegex(InvalidArgumentError, "Invalid arguments for paybill Pay recipient"):
            PayTestCase.pay_obj.add_pay_recipient(payload)

    def test_add_paybill_pay_recipient_without_paybill_account_number_fails(self):
        payload = PAY["invalid_paybill_account_number_paybill"]
        payload.update({"access_token": PayTestCase.ACCESS_TOKEN, "recipient_type": 'paybill'})
        with self.assertRaisesRegex(InvalidArgumentError, "Invalid arguments for paybill Pay recipient"):
            PayTestCase.pay_obj.add_pay_recipient(payload)

    # Send Pay Transaction
    def test_send_pay_to_mobile_wallet_succeeds(self):
        test_payload = {
            "access_token": PayTestCase.ACCESS_TOKEN,
            "destination_reference": '9764ef5f-fcd6-42c1-bbff-de280becc64b',
            "destination_type": 'mobile_wallet',
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "description": "test",
            "amount": '10',
            "currency": 'KES',
            "metadata": { "hey": 'there', "mister": 'dude'}
        }
        self.assertIsNotNone(PayTestCase.pay_obj.send_pay(test_payload))

    def test_create_pay_to_bank_account_succeeds(self):
        test_payload = {
            "access_token": PayTestCase.ACCESS_TOKEN,
            "destination_reference": 'c533cb60-8501-440d-8150-7eaaff84616a',
            "destination_type": 'bank_account',
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "description": "test",
            "amount": '10',
            "currency": 'KES',
            "metadata": { "hey": 'there', "mister": 'dude'}
        }
        self.assertIsNotNone(PayTestCase.pay_obj.send_pay(test_payload))

    def test_create_pay_to_mobile_wallet_returns_resource_url(self):
        test_payload = {
            "access_token": PayTestCase.ACCESS_TOKEN,
            "destination_reference": '9764ef5f-fcd6-42c1-bbff-de280becc64b',
            "destination_type": 'mobile_wallet',
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "description": "test",
            "amount": '10',
            "currency": 'KES',
            "metadata": { "hey": 'there', "mister": 'dude'}
        }
        response = PayTestCase.pay_obj.send_pay(test_payload)
        if self.assertIsNone(PayTestCase.validate(response)) is None:
            PayTestCase.pay_transaction_query_url = response
        self.assertIsNone(PayTestCase.validate(response))

    def test_create_pay_to_bank_account_returns_resource_url(self):
        test_payload = {
            "access_token": PayTestCase.ACCESS_TOKEN,
            "destination_reference": 'c533cb60-8501-440d-8150-7eaaff84616a',
            "destination_type": 'bank_account',
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "description": "test",
            "amount": '10',
            "currency": 'KES',
            "metadata": { "hey": 'there', "mister": 'dude'}
        }
        response = PayTestCase.pay_obj.send_pay(test_payload)
        if self.assertIsNone(PayTestCase.validate(response)) is None:
            PayTestCase.pay_transaction_query_url = response
        self.assertIsNone(PayTestCase.validate(response))

    def test_successful_create_pay_request_to_mobile_wallet(self):
        response = requests.post(
            headers=PayTestCase.header,
            json=json_builder.pay("9764ef5f-fcd6-42c1-bbff-de280becc64b", "mobile_wallet", json_builder.amount('KES', 'python_sdk_value'), "test",
                                  json_builder.links("https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d"),
                                  json_builder.metadata({"cId": '8_675_309', "notes": 'Salary payment May 2018'})),
            data=None,
            url=PayTestCase.pay_obj._build_url(pay.SEND_PAY_PATH))
        self.assertEqual(response.status_code, 201)

    def test_successful_create_pay_request_to_bank_account(self):
        response = requests.post(
            headers=PayTestCase.header,
            json=json_builder.pay("c533cb60-8501-440d-8150-7eaaff84616a", "bank_account", json_builder.amount('KES', 'python_sdk_value'), "test",
                                  json_builder.links("https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d"),
                                  json_builder.metadata({"cId": '8_675_309', "notes": 'Salary payment May 2018'})),
            data=None,
            url=PayTestCase.pay_obj._build_url(pay.SEND_PAY_PATH))
        self.assertEqual(response.status_code, 201)

    # Send Pay Transaction Failure Scenarios
    def test_send_pay_without_destination_reference_fails(self):
        test_payload = {
            "access_token": PayTestCase.ACCESS_TOKEN,
            "destination_type": 'bank_account',
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "amount": '10',
            "description": "test",
            "currency": 'KES',
            "metadata": { "hey": 'there', "mister": 'dude'}
        }
        with self.assertRaisesRegex(InvalidArgumentError, 'Invalid arguments for creating Outgoing Pay.'):
            PayTestCase.pay_obj.send_pay(test_payload)

    def test_send_pay_without_destination_type_fails(self):
        test_payload = {
            "access_token": PayTestCase.ACCESS_TOKEN,
            "destination_reference": '3344-effefnkka-132',
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "amount": '10',
            "description": "test",
            "currency": 'KES',
            "metadata": { "hey": 'there', "mister": 'dude'}
        }
        with self.assertRaisesRegex(InvalidArgumentError, 'Invalid arguments for creating Outgoing Pay.'):
            PayTestCase.pay_obj.send_pay(test_payload)

    def test_send_pay_without_amount_fails(self):
        test_payload = {
            "access_token": PayTestCase.ACCESS_TOKEN,
            "destination_reference": '9764ef5f-fcd6-42c1-bbff-de280becc64b',
            "destination_type": 'mobile_wallet',
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "description": "test",
            "currency": 'KES',
            "metadata": { "hey": 'there', "mister": 'dude'}
        }
        with self.assertRaisesRegex(InvalidArgumentError, 'Invalid arguments for creating Outgoing Pay.'):
            PayTestCase.pay_obj.send_pay(test_payload)

    def test_send_pay_with_invalid_callback_fails(self):
        test_payload = {
            "access_token": PayTestCase.ACCESS_TOKEN,
            "destination_reference": '9764ef5f-fcd6-42c1-bbff-de280becc64b',
            "destination_type": 'mobile_wallet',
            "amount": '10',
            "description": "test",
            "currency": 'KES',
            "metadata": { "hey": 'there', "mister": 'dude'}
        }
        with self.assertRaisesRegex(InvalidArgumentError, 'Invalid arguments for creating Outgoing Pay.'):
            PayTestCase.pay_obj.send_pay(test_payload)

    def test_send_pay_without_description_fails(self):
        test_payload = {
            "access_token": PayTestCase.ACCESS_TOKEN,
            "destination_reference": 'c533cb60-8501-440d-8150-7eaaff84616a',
            "destination_type": 'bank_account',
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "amount": '10',
            "currency": 'KES',
            "metadata": { "hey": 'there', "mister": 'dude'}
        }
        with self.assertRaisesRegex(InvalidArgumentError, 'Invalid arguments for creating Outgoing Pay.'):
            PayTestCase.pay_obj.send_pay(test_payload)

    # Query Status
    # Query Pay Transaction
    def test_pay_transaction_status_succeeds(self):
        self.assertIsNotNone(PayTestCase.pay_obj.pay_transaction_status(PayTestCase.ACCESS_TOKEN,
                                                                        PayTestCase.pay_transaction_query_url))

    def test_pay_transaction_request_status_returns_object(self):
        self.assertIsNotNone(PayTestCase.pay_obj.pay_transaction_status(PayTestCase.ACCESS_TOKEN,
                                                                        PayTestCase.pay_transaction_query_url))

    def test_successful_query_pay_transaction_request(self):
        response = requests.get(
            headers=PayTestCase.header,
            url=PayTestCase.pay_transaction_query_url)
        self.assertEqual(response.status_code, 200)

    # Query Pay Recipient
    def test_pay_recipient_request_status_returns_object(self):
        self.assertIsNotNone(PayTestCase.pay_obj.pay_transaction_status(PayTestCase.ACCESS_TOKEN,
                                                                        PayTestCase.pay_recipient_query_url))

    def test_successful_query_pay_recipient_request(self):
        response = requests.get(
            headers=PayTestCase.header,
            url=PayTestCase.pay_recipient_query_url)
        self.assertEqual(response.status_code, 200)

    # Query Status Failure Scenarios
    def test_pay_transaction_status_with_invalid_query_url_fails(self):
        with self.assertRaises(InvalidArgumentError):
            PayTestCase.pay_obj.pay_transaction_status(
                PayTestCase.ACCESS_TOKEN, "destination")

    def test_pay_transaction_status_with_invalid_access_token_fails(self):
        with self.assertRaises(InvalidArgumentError):
            PayTestCase.pay_obj.pay_transaction_status(
                'access_token', "destination")
