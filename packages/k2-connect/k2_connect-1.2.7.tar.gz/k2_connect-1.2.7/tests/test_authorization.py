import json
import unittest
import requests
from unittest.mock import patch

from k2connect import authorization
from k2connect import exceptions
from mocks import k2_response_mock
from tests import SAMPLE_BASE_URL, SAMPLE_CLIENT_ID, SAMPLE_CLIENT_SECRET
from tests.data import headers


class TokenServiceTestCase(unittest.TestCase):
    token_service_obj = authorization.TokenService(base_url=SAMPLE_BASE_URL, client_id=SAMPLE_CLIENT_ID,
                                                   client_secret=SAMPLE_CLIENT_SECRET)
    header = dict(token_service_obj._headers)

    def test_initialization_with_all_arguments_present_succeeds(self):
        token_service = authorization.TokenService(base_url=SAMPLE_BASE_URL,
                                                   client_id=SAMPLE_CLIENT_ID,
                                                   client_secret=SAMPLE_CLIENT_SECRET)
        self.assertIsInstance(token_service, authorization.TokenService)

    def test_initialization_without_base_url_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            token_service = authorization.TokenService(base_url=None,
                                                       client_id=SAMPLE_CLIENT_ID,
                                                       client_secret=SAMPLE_CLIENT_SECRET)
            self.assertIsInstance(token_service, authorization.TokenService)

    def test_initialization_without_client_id_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            token_service = authorization.TokenService(base_url=SAMPLE_BASE_URL,
                                                       client_id=None,
                                                       client_secret=SAMPLE_CLIENT_SECRET)
            self.assertIsInstance(token_service, authorization.TokenService)

    def test_initialization_without_client_secret_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            token_service = authorization.TokenService(base_url=SAMPLE_BASE_URL,
                                                       client_id=SAMPLE_CLIENT_ID,
                                                       client_secret=None)
            self.assertIsInstance(token_service, authorization.TokenService)

    def test_initialization_without_all_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            token_service = authorization.TokenService(base_url=None,
                                                       client_id=None,
                                                       client_secret=None)
            self.assertIsInstance(token_service, authorization.TokenService)

    def test_successful_create_incoming_payment_request(self):
        response = requests.post(
            headers=TokenServiceTestCase.header,
            params={
                'grant_type': 'client_credentials',
                'client_id': SAMPLE_CLIENT_ID,
                'client_secret': SAMPLE_CLIENT_SECRET,
            },
            data=None,
            url=TokenServiceTestCase.token_service_obj._build_url(authorization.AUTHORIZATION_PATH))
        self.assertEqual(response.status_code, 200)

    def test_request_access_token_returns_response(self):
        response = TokenServiceTestCase.token_service_obj.request_access_token()
        self.assertIsNotNone(response)

    def test_request_access_token_returns_access_token(self):
        token_request = TokenServiceTestCase.token_service_obj.request_access_token()
        access_token = TokenServiceTestCase.token_service_obj.get_access_token(token_request)
        self.assertIsNotNone(access_token)


def return_json_mock_response(path_url):
    with open(path_url) as f:
        return json.load(f)


def token_action(action):
    switcher = {
        "token_info": return_json_mock_response('tests/data/access_token_info.json'),
        "revoke_token": return_json_mock_response('tests/data/revoke_access_token.json'),
        "request_token": return_json_mock_response('tests/data/oauth_access_token.json'),
        "introspect_token": return_json_mock_response('tests/data/access_token_introspect.json')
    }
    return switcher.get(action, "Invalid Token Action")


def assign_mock_response(success_data):
    return k2_response_mock.mock_response(headers=headers.headers, status_code=200, content=success_data,
                                          mock_json=success_data)


def get_mock_success_method(action):
    return "mock_success_" + action + "_response"


class RequestingAccessToken(unittest.TestCase):
    def setUp(self):
        success_data = {}
        token_actions = ["token_info", "revoke_token", "request_token", "introspect_token"]
        for x in token_actions:
            success_data[x] = token_action(x)
            setattr(self, get_mock_success_method(x), assign_mock_response(success_data[x]))

    # @patch('k2connect.authorization.TokenService')
    # def test_request_access_token_returns_response(self, mock_token_service):
    #     token_request = mock_token_service(base_url=SAMPLE_BASE_URL,
    #                                        client_id=SAMPLE_CLIENT_ID,
    #                                        client_secret=SAMPLE_CLIENT_SECRET)
    #
    #     token_request.request_access_token.return_value = self.mock_success_request_token_response
    #
    #     response = token_request.request_access_token()
    #
    #     self.assertIsNotNone(response)

    @patch('k2connect.authorization.TokenService')
    def test_request_access_token_returns_access_token(self, mock_token_service):
        token_request = mock_token_service(base_url=SAMPLE_BASE_URL,
                                           client_id=SAMPLE_CLIENT_ID,
                                           client_secret=SAMPLE_CLIENT_SECRET)
        token_request.request_access_token.return_value = self.mock_success_request_token_response
        response = token_request.request_access_token()
        access_token = response.body.get('access_token')
        self.assertIsNotNone(access_token)

    @patch('k2connect.authorization.TokenService')
    def test_revoke_access_token_returns_response(self, mock_token_service):
        token_request = mock_token_service(base_url=SAMPLE_BASE_URL,
                                           client_id=SAMPLE_CLIENT_ID,
                                           client_secret=SAMPLE_CLIENT_SECRET)
        token_request.request_access_token.return_value = self.mock_success_request_token_response
        token_request.revoke_access_token.return_value = self.mock_success_revoke_token_response
        access_token_response = token_request.request_access_token()
        access_token = access_token_response.body.get('access_token')
        response = token_request.revoke_access_token(access_token)
        self.assertIsNotNone(response)

    @patch('k2connect.authorization.TokenService')
    def test_revoke_access_token_returns_status_200(self, mock_token_service):
        token_request = mock_token_service(base_url=SAMPLE_BASE_URL,
                                           client_id=SAMPLE_CLIENT_ID,
                                           client_secret=SAMPLE_CLIENT_SECRET)
        token_request.request_access_token.return_value = self.mock_success_request_token_response
        token_request.revoke_access_token.return_value = self.mock_success_revoke_token_response
        access_token_response = token_request.request_access_token()
        response = token_request.revoke_access_token(access_token_response.body.get('access_token'))
        self.assertEqual(response.status_code, 200)

    @patch('k2connect.authorization.TokenService')
    def test_introspect_access_token_returns_response(self, mock_token_service):
        token_request = mock_token_service(base_url=SAMPLE_BASE_URL,
                                           client_id=SAMPLE_CLIENT_ID,
                                           client_secret=SAMPLE_CLIENT_SECRET)
        token_request.request_access_token.return_value = self.mock_success_request_token_response
        token_request.introspect_access_token.return_value = self.mock_success_introspect_token_response
        access_token_response = token_request.request_access_token()
        access_token = access_token_response.body.get('access_token')
        response = token_request.introspect_access_token(access_token)
        self.assertIsNotNone(response)

    @patch('k2connect.authorization.TokenService')
    def test_introspect_access_token_returns_status_200(self, mock_token_service):
        token_request = mock_token_service(base_url=SAMPLE_BASE_URL,
                                           client_id=SAMPLE_CLIENT_ID,
                                           client_secret=SAMPLE_CLIENT_SECRET)
        token_request.request_access_token.return_value = self.mock_success_request_token_response
        token_request.introspect_access_token.return_value = self.mock_success_introspect_token_response
        access_token_response = token_request.request_access_token()
        response = token_request.introspect_access_token(access_token_response.body.get('access_token'))
        self.assertEqual(response.status_code, 200)

    @patch('k2connect.authorization.TokenService')
    def test_access_token_info_returns_response(self, mock_token_service):
        token_request = mock_token_service(base_url=SAMPLE_BASE_URL,
                                           client_id=SAMPLE_CLIENT_ID,
                                           client_secret=SAMPLE_CLIENT_SECRET)
        token_request.request_access_token.return_value = self.mock_success_request_token_response
        token_request.request_token_info.return_value = self.mock_success_token_info_response
        access_token_response = token_request.request_access_token()
        access_token = access_token_response.body.get('access_token')
        response = token_request.request_token_info(access_token)
        self.assertIsNotNone(response)

    @patch('k2connect.authorization.TokenService')
    def test_access_token_info_returns_status_200(self, mock_token_service):
        token_request = mock_token_service(base_url=SAMPLE_BASE_URL,
                                           client_id=SAMPLE_CLIENT_ID,
                                           client_secret=SAMPLE_CLIENT_SECRET)
        token_request.request_access_token.return_value = self.mock_success_request_token_response
        token_request.request_token_info.return_value = self.mock_success_token_info_response
        access_token_response = token_request.request_access_token()
        response = token_request.request_token_info(access_token_response.body.get('access_token'))
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        token_actions = ["token_info", "revoke_token", "request_token", "introspect_token"]
        for method_name, action in zip(dir(self), token_actions):
            if callable(getattr(self, method_name)) and action in method_name:
                self.method_name.dispose()


if __name__ == '__main__':
    INITIALIZATION_SUITE = unittest.TestLoader().loadTestsFromTestCase(TokenServiceTestCase)
    REQUEST_ACCESS_TOKEN_SUITE = unittest.TestLoader().loadTestsFromTestCase(RequestingAccessToken)
    PARENT_SUITE = unittest.TestSuite([INITIALIZATION_SUITE, REQUEST_ACCESS_TOKEN_SUITE])
    unittest.TextTestRunner(verbosity=1).run(PARENT_SUITE)
