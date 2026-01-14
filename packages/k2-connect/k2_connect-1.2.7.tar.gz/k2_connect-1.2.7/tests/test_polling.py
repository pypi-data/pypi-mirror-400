import requests
import unittest
from urlvalidator import URLValidator

from k2connect import polling, authorization, json_builder, exceptions, validation
from k2connect.exceptions import InvalidArgumentError
from tests import SAMPLE_BASE_URL, SAMPLE_CLIENT_ID, SAMPLE_CLIENT_SECRET


class PollingTestCase(unittest.TestCase):
    polling_url = ''
    # Establish environment
    validate = URLValidator()

    token_service = authorization.TokenService(SAMPLE_BASE_URL, SAMPLE_CLIENT_ID, SAMPLE_CLIENT_SECRET)
    access_token_request = token_service.request_access_token()
    ACCESS_TOKEN = token_service.get_access_token(access_token_request)

    polling_obj = polling.PollingService(base_url=SAMPLE_BASE_URL)
    header = dict(polling_obj._headers)
    header['Authorization'] = 'Bearer ' + ACCESS_TOKEN

    def test_init_method_with_base_url_argument_succeeds(self):
        transaction_notifications_service = polling.PollingService(base_url=SAMPLE_BASE_URL)
        self.assertIsInstance(transaction_notifications_service, polling.PollingService)

    def test_init_method_without_base_url_argument_fails(self):
        self.assertRaises(TypeError, lambda: polling.PollingService())

    # Transaction Notification transaction_notifications
    def test_create_polling_request_returns_resource_url(self):
        test_payload = {
            "access_token": PollingTestCase.ACCESS_TOKEN,
            "callback_url": 'https://webhook.site/48d6113c-8967-4bf4-ab56-dcf470e0b005',
            "scope": "till",
            "scope_reference": "112233",
            "from_time": "2021-07-09T08:50:22+03:00",
            "to_time": "2021-07-10T18:00:22+03:00",
        }
        response = PollingTestCase.polling_obj.create_polling_request(test_payload)
        if self.assertIsNone(PollingTestCase.validate(response)) is None:
            PollingTestCase.polling_url = response
        self.assertIsNone(PollingTestCase.validate(response))

    # Query Request
    def test_successfully_sent_transaction_sms_notification_status_succeeds(self):
        self.assertIsNotNone(
            PollingTestCase.polling_obj.polling_request_status(
                PollingTestCase.ACCESS_TOKEN,
                PollingTestCase.polling_url))

    def test_successfully_sent_transaction_sms_notification_status_request(self):
        response = requests.get(
            headers=PollingTestCase.header,
            url=PollingTestCase.polling_url)
        self.assertEqual(response.status_code, 200)

    # Failure scenarios
