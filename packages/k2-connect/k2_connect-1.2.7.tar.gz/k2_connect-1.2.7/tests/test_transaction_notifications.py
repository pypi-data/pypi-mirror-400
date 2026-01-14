import requests
import unittest
from urlvalidator import URLValidator

from k2connect import notifications, authorization, json_builder, exceptions, validation
from k2connect.exceptions import InvalidArgumentError
from tests import SAMPLE_BASE_URL, SAMPLE_CLIENT_ID, SAMPLE_CLIENT_SECRET


class TransactionNotificationsTestCase(unittest.TestCase):
    transaction_notifications_url = ''
    # Establish environment
    validate = URLValidator()

    token_service = authorization.TokenService(SAMPLE_BASE_URL, SAMPLE_CLIENT_ID, SAMPLE_CLIENT_SECRET)
    access_token_request = token_service.request_access_token()
    ACCESS_TOKEN = token_service.get_access_token(access_token_request)

    transaction_notifications_obj = notifications.NotificationService(base_url=SAMPLE_BASE_URL)
    header = dict(transaction_notifications_obj._headers)
    header['Authorization'] = 'Bearer ' + ACCESS_TOKEN

    def test_init_method_with_base_url_argument_succeeds(self):
        transaction_notifications_service = notifications.NotificationService(base_url=SAMPLE_BASE_URL)
        self.assertIsInstance(transaction_notifications_service, notifications.NotificationService)

    def test_init_method_without_base_url_argument_fails(self):
        self.assertRaises(TypeError, lambda: notifications.NotificationService())

    # Transaction Notification transaction_notifications
    def test_sending_transaction_sms_notification_succeeds(self):
        test_payload = {
            "access_token": TransactionNotificationsTestCase.ACCESS_TOKEN,
            "callback_url": 'https://webhook.site/48d6113c-8967-4bf4-ab56-dcf470e0b005',
            "webhook_event_reference": "d81312b9-4c0e-4347-971f-c3d5b14bdbe4",
            "message": 'Alleluia',
        }
        self.assertIsNotNone(
            TransactionNotificationsTestCase.transaction_notifications_obj.send_transaction_sms_notification(test_payload))

    def test_sending_transaction_sms_notification_returns_resource_url(self):
        test_payload = {
            "access_token": TransactionNotificationsTestCase.ACCESS_TOKEN,
            "callback_url": 'https://webhook.site/48d6113c-8967-4bf4-ab56-dcf470e0b005',
            "webhook_event_reference": "d81312b9-4c0e-4347-971f-c3d5b14bdbe4",
            "message": 'Alleluia',
        }
        response = TransactionNotificationsTestCase.transaction_notifications_obj.send_transaction_sms_notification(test_payload)
        if self.assertIsNone(TransactionNotificationsTestCase.validate(response)) is None:
            TransactionNotificationsTestCase.transaction_notifications_url = response
        self.assertIsNone(TransactionNotificationsTestCase.validate(response))

    # Query Request
    def test_successfully_sent_transaction_sms_notification_status_succeeds(self):
        self.assertIsNotNone(
            TransactionNotificationsTestCase.transaction_notifications_obj.transaction_notification_status(
                TransactionNotificationsTestCase.ACCESS_TOKEN,
                TransactionNotificationsTestCase.transaction_notifications_url))

    def test_successfully_sent_transaction_sms_notification_status_request(self):
        response = requests.get(
            headers=TransactionNotificationsTestCase.header,
            url=TransactionNotificationsTestCase.transaction_notifications_url)
        self.assertEqual(response.status_code, 200)

    # Failure scenarios
