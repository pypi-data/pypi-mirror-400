import requests
import unittest
from urlvalidator import URLValidator

from k2connect import webhooks, authorization, json_builder, exceptions, validation
from k2connect.exceptions import InvalidArgumentError
from tests import SAMPLE_BASE_URL, SAMPLE_WEBHOOK_SECRET, SAMPLE_CLIENT_ID, SAMPLE_CLIENT_SECRET


class WebhooksTestCase(unittest.TestCase):
    # Establish environment
    validate = URLValidator()
    
    token_service = authorization.TokenService(SAMPLE_BASE_URL, SAMPLE_CLIENT_ID, SAMPLE_CLIENT_SECRET)
    access_token_request = token_service.request_access_token()
    ACCESS_TOKEN = token_service.get_access_token(access_token_request)

    webhook_obj = webhooks.WebhookService(base_url=SAMPLE_BASE_URL)
    header = dict(webhook_obj._headers)
    header['Authorization'] = 'Bearer ' + ACCESS_TOKEN

    def test_init_method_with_base_url_argument_succeeds(self):
        webhook_service = webhooks.WebhookService(base_url=SAMPLE_BASE_URL)
        self.assertIsInstance(webhook_service, webhooks.WebhookService)

    # Test Request Status
    def test_create_buygoods_webhook_subscription_request_succeeds(self):
        response = requests.post(
            headers=WebhooksTestCase.header,
            json=json_builder.webhook_subscription("buygoods_transaction_received",
                                                   "https://webhook.site/dcbdce14-dd4f-4493-be2c-ad3526354fa8",
                                                   'till', '112233'),
            data=None,
            url=WebhooksTestCase.webhook_obj._build_url(webhooks.WEBHOOK_SUBSCRIPTION_PATH),)
        self.assertEqual(response.status_code, 201)

    def test_create_b2b_webhook_subscription_request_succeeds(self):
        response = requests.post(
            headers=WebhooksTestCase.header,
            json=json_builder.webhook_subscription("b2b_transaction_received",
                                                   "https://webhook.site/dcbdce14-dd4f-4493-be2c-ad3526354fa8",
                                                   'till', '112233'),
            data=None,
            url=WebhooksTestCase.webhook_obj._build_url(webhooks.WEBHOOK_SUBSCRIPTION_PATH),)
        self.assertEqual(response.status_code, 201)

    def test_create_buygoods_reversal_webhook_subscription_request_succeeds(self):
        response = requests.post(
            headers=WebhooksTestCase.header,
            json=json_builder.webhook_subscription("buygoods_transaction_reversed",
                                                   "https://webhook.site/dcbdce14-dd4f-4493-be2c-ad3526354fa8",
                                                   'till', '112233'),
            data=None,
            url=WebhooksTestCase.webhook_obj._build_url(webhooks.WEBHOOK_SUBSCRIPTION_PATH),)
        self.assertEqual(response.status_code, 201)

    def test_create_customer_created_webhook_subscription_request_succeeds(self):
        response = requests.post(
            headers=WebhooksTestCase.header,
            json=json_builder.webhook_subscription("customer_created",
                                                   "https://webhook.site/dcbdce14-dd4f-4493-be2c-ad3526354fa8",
                                                   'company'),
            data=None,
            url=WebhooksTestCase.webhook_obj._build_url(webhooks.WEBHOOK_SUBSCRIPTION_PATH),)
        self.assertEqual(response.status_code, 201)

    def test_create_settlement_transfer_webhook_subscription_request_succeeds(self):
        response = requests.post(
            headers=WebhooksTestCase.header,
            json=json_builder.webhook_subscription("settlement_transfer_completed",
                                                   "https://webhook.site/dcbdce14-dd4f-4493-be2c-ad3526354fa8",
                                                   'company'),
            data=None,
            url=WebhooksTestCase.webhook_obj._build_url(webhooks.WEBHOOK_SUBSCRIPTION_PATH),)
        self.assertEqual(response.status_code, 201)

    def test_create_m2m_transaction_received_webhook_subscription_request_succeeds(self):
        response = requests.post(
            headers=WebhooksTestCase.header,
            json=json_builder.webhook_subscription("m2m_transaction_received",
                                                   "https://webhook.site/dcbdce14-dd4f-4493-be2c-ad3526354fa8",
                                                   'company'),
            data=None,
            url=WebhooksTestCase.webhook_obj._build_url(webhooks.WEBHOOK_SUBSCRIPTION_PATH),)
        self.assertEqual(response.status_code, 201)

    # Test that module successfully creates and sends the request
    def test_create_buygoods_webhook_succeeds(self):
        test_payload = {
            "access_token": WebhooksTestCase.ACCESS_TOKEN,
            "event_type": 'buygoods_transaction_received',
            "webhook_endpoint": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "scope": 'till',
            "scope_reference": '112233'
        }
        self.assertIsNotNone(webhooks.WebhookService(base_url=SAMPLE_BASE_URL).create_subscription(test_payload))

    def test_create_b2b_webhook_succeeds(self):
        test_payload = {
            "access_token": WebhooksTestCase.ACCESS_TOKEN,
            "event_type": 'b2b_transaction_received',
            "webhook_endpoint": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "scope": 'till',
            "scope_reference": '112233'
        }
        self.assertIsNotNone(webhooks.WebhookService(base_url=SAMPLE_BASE_URL).create_subscription(test_payload))

    def test_create_buygoods_reversal_webhook_succeeds(self):
        test_payload = {
            "access_token": WebhooksTestCase.ACCESS_TOKEN,
            "event_type": 'buygoods_transaction_reversed',
            "webhook_endpoint": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "scope": 'till',
            "scope_reference": '112233'
        }
        self.assertIsNotNone(webhooks.WebhookService(base_url=SAMPLE_BASE_URL).create_subscription(test_payload))

    def test_create_customer_created_succeeds(self):
        test_payload = {
            "access_token": WebhooksTestCase.ACCESS_TOKEN,
            "event_type": 'customer_created',
            "webhook_endpoint": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "scope": 'company'
        }
        self.assertIsNotNone(webhooks.WebhookService(base_url=SAMPLE_BASE_URL).create_subscription(test_payload))

    def test_create_settlement_transfer_webhook_succeeds(self):
        test_payload = {
            "access_token": WebhooksTestCase.ACCESS_TOKEN,
            "event_type": 'settlement_transfer_completed',
            "webhook_endpoint": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "scope": 'company'
        }
        self.assertIsNotNone(webhooks.WebhookService(base_url=SAMPLE_BASE_URL).create_subscription(test_payload))

    def test_create_m2m_transaction_received_webhook_succeeds(self):
        test_payload = {
            "access_token": WebhooksTestCase.ACCESS_TOKEN,
            "event_type": 'm2m_transaction_received',
            "webhook_endpoint": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "scope": 'company'
        }
        self.assertIsNotNone(webhooks.WebhookService(base_url=SAMPLE_BASE_URL).create_subscription(test_payload))

    # Test it returns the resource_url
    def test_buygoods_webhook_subscription_returns_resource_url(self):
        test_payload = {
            "access_token": WebhooksTestCase.ACCESS_TOKEN,
            "event_type": 'buygoods_transaction_received',
            "webhook_endpoint": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "scope": 'till',
            "scope_reference": '112233'
        }
        response = webhooks.WebhookService(base_url=SAMPLE_BASE_URL).create_subscription(test_payload)
        self.assertIsNone(WebhooksTestCase.validate(response))

    def test_b2b_webhook_subscription_returns_resource_url(self):
        test_payload = {
            "access_token": WebhooksTestCase.ACCESS_TOKEN,
            "event_type": 'b2b_transaction_received',
            "webhook_endpoint": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "scope": 'till',
            "scope_reference": '112233'
        }
        response = webhooks.WebhookService(base_url=SAMPLE_BASE_URL).create_subscription(test_payload)
        self.assertIsNone(WebhooksTestCase.validate(response))

    def test_buygoods_reversal_webhook_subscription_returns_resource_url(self):
        test_payload = {
            "access_token": WebhooksTestCase.ACCESS_TOKEN,
            "event_type": 'buygoods_transaction_reversed',
            "webhook_endpoint": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "scope": 'till',
            "scope_reference": '112233'
        }
        response = webhooks.WebhookService(base_url=SAMPLE_BASE_URL).create_subscription(test_payload)
        self.assertIsNone(WebhooksTestCase.validate(response))

    def test_customer_created_webhook_subscription_returns_resource_url(self):
        test_payload = {
            "access_token": WebhooksTestCase.ACCESS_TOKEN,
            "event_type": 'customer_created',
            "webhook_endpoint": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "scope": 'company'
        }
        response = webhooks.WebhookService(base_url=SAMPLE_BASE_URL).create_subscription(test_payload)
        self.assertIsNone(WebhooksTestCase.validate(response))

    def test_settlement_transfer_webhook_subscription_returns_resource_url(self):
        test_payload = {
            "access_token": WebhooksTestCase.ACCESS_TOKEN,
            "event_type": 'settlement_transfer_completed',
            "webhook_endpoint": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "scope": 'company'
        }
        response = webhooks.WebhookService(base_url=SAMPLE_BASE_URL).create_subscription(test_payload)
        self.assertIsNone(WebhooksTestCase.validate(response))

    def test_m2m_webhook_subscription_returns_resource_url(self):
        test_payload = {
            "access_token": WebhooksTestCase.ACCESS_TOKEN,
            "event_type": 'm2m_transaction_received',
            "webhook_endpoint": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "scope": 'company'
        }
        response = webhooks.WebhookService(base_url=SAMPLE_BASE_URL).create_subscription(test_payload)
        self.assertIsNone(WebhooksTestCase.validate(response))

    # Test Failure scenarios
    def test_create_invalid_webhook_fails(self):
        test_payload = {
            "access_token": WebhooksTestCase.ACCESS_TOKEN,
            "event_type": 'settlement',
            "webhook_endpoint": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "webhook_secret": SAMPLE_WEBHOOK_SECRET,
            "scope": 'Till',
            "scope_reference": '112233'
        }
        with self.assertRaises(InvalidArgumentError):
            webhooks.WebhookService(base_url=SAMPLE_BASE_URL).create_subscription(test_payload)

    def test_create_invalid_till_scope_webhook_fails(self):
        test_payload = {
            "access_token": WebhooksTestCase.ACCESS_TOKEN,
            "event_type": 'b2b_transaction_received',
            "webhook_endpoint": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "scope": 'company'
        }
        with self.assertRaisesRegex(InvalidArgumentError, "Invalid scope for given event type."):
            webhooks.WebhookService(base_url=SAMPLE_BASE_URL).create_subscription(test_payload)

    def test_create_till_scope_webhook_with_no_scope_reference_fails(self):
        test_payload = {
            "access_token": WebhooksTestCase.ACCESS_TOKEN,
            "event_type": 'b2b_transaction_received',
            "webhook_endpoint": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "scope": 'till'
        }
        with self.assertRaisesRegex(InvalidArgumentError, 'Scope reference not given.'):
            webhooks.WebhookService(base_url=SAMPLE_BASE_URL).create_subscription(test_payload)

    def test_create_invalid_company_scope_webhook_fails(self):
        test_payload = {
            "access_token": WebhooksTestCase.ACCESS_TOKEN,
            "event_type": 'settlement_transfer_completed',
            "webhook_endpoint": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "scope": 'till',
            "scope_reference": '112233'
        }
        with self.assertRaisesRegex(InvalidArgumentError, "Invalid scope for given event type."):
            webhooks.WebhookService(base_url=SAMPLE_BASE_URL).create_subscription(test_payload)
