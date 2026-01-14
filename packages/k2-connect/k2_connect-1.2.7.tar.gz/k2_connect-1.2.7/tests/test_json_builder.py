import unittest

from k2connect import exceptions
from k2connect import json_builder
from tests import SAMPLE_DICTIONARY


class SerializerMethodTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.sample_serialized_json = json_builder.serializer(SAMPLE_DICTIONARY)

    def test_serializer_method_with_dictionary_argument_succeeds(self):
        self.assertIsNotNone(self.sample_serialized_json)

    def test_serializer_method_with_dictionary_argument_returns_json_str(self):
        self.assertIsInstance(self.sample_serialized_json, str)

    def test_serializer_method_without_dictionary_argument_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.serializer(dictionary=None)

    def test_serializer_method_without_type_dict_argument_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.serializer(dictionary=100)


class MetadataMethodTestCase(unittest.TestCase):

    def test_metadata_method_with_kwargs_succeeds(self):
        metadata_json = json_builder.metadata(name='Brandon Stark')
        self.assertIsNotNone(metadata_json)

    def test_metadata_method_without_kwargs_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.metadata(None)

    def test_metadata_method_with_more_than_five_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.metadata(title1='Mother of dragons',
                                  title2='The unburnt',
                                  title3='Breaker of chains',
                                  title4='Khaleesi',
                                  title5='Queen of the Andals',
                                  title6='Protector of the realm')


class LinksMethodTestCase(unittest.TestCase):

    def test_link_method_with_callback_url_argument_succeeds(self):
        links_json = json_builder.links(callback_url='https://some-westoros-url.got')
        self.assertIsNotNone(links_json)

    def test_link_method_without_callback_url_argument_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.links(callback_url=None)

    def test_link_method_with_empty_string_argument_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.links(callback_url='')

    def test_link_method_with_non_str_argument_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.links(callback_url={'Igret': 'You know nothing Jon Snow'})


class AmountMethodTestCase(unittest.TestCase):

    def test_amount_method_with_all_arguments_succeeds(self):
        amount_json = json_builder.amount(currency='Gold',
                                          value='50000')
        self.assertIsNotNone(amount_json)

    def test_amount_method_without_any_argument_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.amount(currency=None, value=None)

    def test_amount_method_without_currency_argument_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.amount(currency=None, value='50000')

    def test_amount_method_without_value_argument_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.amount(currency='Gold', value=None)

    def test_amount_method_with_empty_string_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.amount(currency='', value='')

    def test_amount_method_with_empty_string_currency_argument_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.amount(currency='', value='50000')

    def test_amount_method_with_empty_string_value_argument_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.amount(currency='Gold', value='')

    def test_amount_method_with_non_str_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.amount(currency=950, value=['Esos', 'Westoros'])

    def test_amount_method_with_non_str_currency_argument_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.amount(currency=500, value='50000')

    def test_amount_method_with_non_str_value_argument_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.amount(currency='Gold', value=['Esos', 'Westoros'])


class BankAccountMethodTestCase(unittest.TestCase):

    def test_bank_account_method_with_all_required_arguments_succeeds(self):
        bank_account_json = json_builder.bank_account(first_name='Stannis',
                                                      last_name='Baratheon',
                                                      account_name='Stannis Baratheon',
                                                      account_number='IRNBNK0056',
                                                      bank_branch_id='IRNBNKBRAVOS875',
                                                      bank_id='78456',
                                                      name='Stannis Baratheon')
        self.assertIsNotNone(bank_account_json)

    def test_bank_account_method_with_all_required_arguments_plus_permitted_kwargs_succeeds(self):
        bank_account_json = json_builder.bank_account(first_name='Stannis',
                                                      last_name='Baratheon',
                                                      account_name='Stannis Baratheon',
                                                      account_number='IRNBNK0056',
                                                      bank_branch_id='IRNBNKBRAVOS875',
                                                      bank_id='78456',
                                                      name='Stannis Baratheon',
                                                      email='Stannis@irn.com',
                                                      phone='+87546214588')
        self.assertIsNotNone(bank_account_json)

    def test_bank_account_method_with_all_required_arguments_plus_email_succeeds(self):
        bank_account_json = json_builder.bank_account(first_name='Stannis',
                                                      last_name='Baratheon',
                                                      account_name='Stannis Baratheon',
                                                      account_number='IRNBNK0056',
                                                      bank_branch_id='IRNBNKBRAVOS875',
                                                      bank_id='78456',
                                                      name='Stannis Baratheon',
                                                      email='Stannis@irn.com')
        self.assertIsNotNone(bank_account_json)

    def test_bank_account_method_with_all_required_arguments_plus_phone_succeeds(self):
        bank_account_json = json_builder.bank_account(first_name='Stannis',
                                                      last_name='Baratheon',
                                                      account_name='Stannis Baratheon',
                                                      account_number='IRNBNK0056',
                                                      bank_branch_id='IRNBNKBRAVOS875',
                                                      bank_id='78456',
                                                      name='Stannis Baratheon',
                                                      phone='+87546214588')
        self.assertIsNotNone(bank_account_json)

    def test_bank_account_method_without_required_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.bank_account(first_name=None,
                                      last_name=None,
                                      account_name=None,
                                      account_number=None,
                                      bank_branch_id=None,
                                      bank_id=None,
                                      name=None)

    def test_bank_account_method_with_non_str_required_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.bank_account(first_name='Stannis',
                                      last_name='Baratheon',
                                      account_name=1547,
                                      account_number={'Arya Strak': 'The North remembers'},
                                      bank_branch_id=('Father', 'Smith', 'Warrior'),
                                      bank_id=['Mother', 'Maiden', 'Crone'],
                                      name=89.235)


class BankSettlementAccountTestCase(unittest.TestCase):
    def test_bank_settlement_account_method_with_all_required_arguments_succeeds(self):
        bank_settlement_account_json = json_builder.bank_settlement_account(account_name='Stannis Baratheon',
                                                                            account_number='IRNBNK0056',
                                                                            bank_id='78456',
                                                                            bank_branch_id='IRNBNKBRAVOS875')
        self.assertIsNotNone(bank_settlement_account_json)

    def test_bank_settlement_account_method_without_required_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.bank_settlement_account(account_name=None,
                                                 account_number=None,
                                                 bank_id=None,
                                                 bank_branch_id=None)

    def test_bank_settlement_account_method_with_non_str_required_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.bank_settlement_account(account_name=456987,
                                                 account_number=456987,
                                                 bank_id=456987,
                                                 bank_branch_id=456987)


class MobileWalletMethodTestCase(unittest.TestCase):
    def test_mobile_wallet_method_with_all_required_arguments_succeeds(self):
        mobile_wallet_json = json_builder.mobile_wallet(first_name='Jon',
                                                        last_name='Snow',
                                                        phone='+89456137822',
                                                        network='EsosTel')
        self.assertIsNotNone(mobile_wallet_json)

    def test_mobile_wallet_method_without_required_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.mobile_wallet(first_name=None,
                                       last_name=None,
                                       phone=None,
                                       network=None)

    def test_mobile_wallet_method_with_non_str_required_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.mobile_wallet(first_name=124578,
                                       last_name=124578,
                                       phone=124578,
                                       network=124578)


class PayRecipientMethodTestCase(unittest.TestCase):
    def test_pay_recipient_method_with_all_required_arguments_succeeds(self):
        pay_recipient_json = json_builder.pay_recipient(recipient_type='mobile wallet',
                                                        recipient='{"name": "Stannis Baratheon "}')
        self.assertIsNotNone(pay_recipient_json)

    def test_pay_recipient_method_without_required_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.pay_recipient(recipient_type=None,
                                       recipient=None)

    def test_pay_recipient_method_with_non_str_required_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.pay_recipient(recipient_type=1245,
                                       recipient=12345)


class SubscriberMethodTestCase(unittest.TestCase):
    def test_subscriber_method_with_all_required_arguments_succeeds(self):
        subscriber_json = json_builder.subscriber(first_name='Jon',
                                                  last_name='Snow',
                                                  phone='+89456137822', )
        self.assertIsNotNone(subscriber_json)

    def test_subscriber_method_without_required_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.subscriber(first_name=None,
                                    last_name=None,
                                    phone=None)

    def test_subscriber_method_with_non_str_required_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.subscriber(first_name=98745,
                                    last_name=98745,
                                    phone=98745)


class MpesaPaymentMethodTestCase(unittest.TestCase):
    def test_mpesa_payment_method_with_all_required_arguments_succeeds(self):
        mpesa_payment_json = json_builder.mpesa_payment(mpesa_links='sample_mpesa_links',
                                                        mpesa_payment_amount='sample_mpesa_payment_amount',
                                                        mpesa_payment_subscriber='sample_mpesa_payment_subscriber',
                                                        payment_channel='sample_payment_channel',
                                                        till_number='sample_till_number')
        self.assertIsNotNone(mpesa_payment_json)

    def test_mpesa_payment_method_without_required_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            mpesa_payment_amount = json_builder.amount(currency=None,
                                                               value=None)
            mpesa_links = json_builder.links(callback_url=None)
            mpesa_payment_metadata = json_builder.metadata(**{None: None})
            mpesa_payment_subscriber = json_builder.subscriber(first_name=None,
                                                               last_name=None,
                                                               phone=None,
                                                               email=None)
            json_builder.mpesa_payment(mpesa_links,
                                       mpesa_payment_amount,
                                       mpesa_payment_subscriber,
                                       None,
                                       None)

    def test_mpesa_payment_method_with_non_str_required_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            mpesa_payment_amount = json_builder.amount(currency=15462,
                                                               value=15462)
            mpesa_links = json_builder.links(callback_url=15462)
            mpesa_payment_metadata = json_builder.metadata(**{15462: 15462})
            mpesa_payment_subscriber = json_builder.subscriber(first_name=15462,
                                                               last_name=15462,
                                                               phone=15462,
                                                               email=15462)
            json_builder.mpesa_payment(mpesa_links,
                                       mpesa_payment_amount,
                                       mpesa_payment_subscriber,
                                       15462,
                                       15462)


class WebhookSubscriptionMethodTestCase(unittest.TestCase):
    def test_webhook_subscription_method_with_all_required_arguments_succeeds(self):
        webhook_subscription_json = json_builder.webhook_subscription(event_type='sample_event_type',
                                                                      webhook_endpoint='sample_webhook_endpoint',
                                                                      webhook_secret='sample_webhook_secret')
        self.assertIsNotNone(webhook_subscription_json)

    def test_webhook_subscription_method_without_required_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.webhook_subscription(event_type=None,
                                              webhook_endpoint=None,
                                              webhook_secret=None)

    def test_webhook_subscription_method_with_non_str_required_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            json_builder.webhook_subscription(event_type=12457,
                                              webhook_endpoint=12457,
                                              webhook_secret=12457)


class PayMethodTestCase(unittest.TestCase):
    def test_pay_method_with_all_required_arguments_succeeds(self):
        pay_json = json_builder.pay(payment_destination='sample_payment_destination',
                                    payment_amount='sample_payment_amount',
                                    payment_metadata='sample_payment_metadata',
                                    payment_links='sample_payment_links')
        self.assertIsNotNone(pay_json)

    def test_pay_method_without_required_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            payment_amount = json_builder.amount(currency=None,
                                                 value=None)
            payment_metadata = json_builder.metadata(**{12457: None})
            payment_links = json_builder.links(callback_url=None)
            json_builder.pay(None,
                             payment_amount,
                             payment_metadata,
                             payment_links)

    def test_pay_method_with_non_str_required_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            payment_amount = json_builder.amount(currency=12457,
                                                 value=12457)
            payment_metadata = json_builder.metadata(**{12457: 12457})
            payment_links = json_builder.links(callback_url=12457)
            json_builder.pay(12457,
                             payment_amount,
                             payment_metadata,
                             payment_links)


class TransfersMethodTestCase(unittest.TestCase):
    def test_transfers_method_with_all_required_arguments_succeeds(self):
        transfers_json = json_builder.transfers(transfer_links='sample_transfer_links',
                                                transfers_amount='sample_transfers_amount')
        self.assertIsNotNone(transfers_json)

    def test_transfers_method_without_required_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            transfers_amount = json_builder.amount(currency=None,
                                                  value=None)
            transfer_links = json_builder.links(callback_url=None)
            json_builder.transfers(transfer_links, transfers_amount)

    def test_transfers_method_with_non_str_required_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            transfers_amount = json_builder.amount(currency=145524,
                                                  value=145524)
            transfer_links = json_builder.links(callback_url=145524)
            json_builder.transfers(transfer_links, transfers_amount)


if __name__ == '__main__':
    SERIALIZER_METHOD_TEST_SUITE = unittest.TestLoader().loadTestsFromTestCase(SerializerMethod)
    METADATA_METHOD_TEST_SUITE = unittest.TestLoader().loadTestsFromTestCase(MetadataMethod)
    LINKS_METHOD_TEST_SUITE = unittest.TestLoader().loadTestsFromTestCase(LinksMethod)
    AMOUNT_METHOD_TEST_SUITE = unittest.TestLoader().loadTestsFromTestCase(AmountMethodTestCase)
    BANK_ACCOUNT_METHOD_TEST_SUITE = unittest.TestLoader().loadTestsFromTestCase(BankAccountMethodTestCase)
    BANK_SETTLEMENT_AMOUNT_METHOD_TEST_SUITE = unittest.TestLoader().loadTestsFromTestCase(
        BankSettlementAccountTestCase)
    MOBILE_WALLET_TEST_SUITE = unittest.TestLoader().loadTestsFromTestCase(MobileWalletMethodTestCase)
    PAY_RECIPIENT_TEST_SUITE = unittest.TestLoader().loadTestsFromTestCase(PayRecipientMethodTestCase)
    SUBSCRIBER_TEST_SUITE = unittest.TestLoader().loadTestsFromTestCase(SubscriberMethodTestCase)
    MPESA_PAYMENT_TEST_SUITE = unittest.TestLoader().loadTestsFromTestCase(MpesaPaymentMethodTestCase)
    WEBHOOK_SUBSCRIPTION_TEST_SUITE = unittest.TestLoader().loadTestsFromTestCase(WebhookSubscriptionMethodTestCase)
    PAY_TEST_SUITE = unittest.TestLoader().loadTestsFromTestCase(PayMethodTestCase)
    TRANSFERS_TEST_SUITE = unittest.TestLoader().loadTestsFromTestCase(TransfersMethodTestCase)
    PARENT_SUITE = unittest.TestSuite(
        [SERIALIZER_METHOD_TEST_SUITE,
         METADATA_METHOD_TEST_SUITE,
         LINKS_METHOD_TEST_SUITE,
         AMOUNT_METHOD_TEST_SUITE,
         BANK_ACCOUNT_METHOD_TEST_SUITE,
         BANK_SETTLEMENT_AMOUNT_METHOD_TEST_SUITE,
         MOBILE_WALLET_TEST_SUITE,
         PAY_RECIPIENT_TEST_SUITE,
         SUBSCRIBER_TEST_SUITE,
         MPESA_PAYMENT_TEST_SUITE,
         WEBHOOK_SUBSCRIPTION_TEST_SUITE,
         PAY_TEST_SUITE,
         TRANSFERS_TEST_SUITE])
    unittest.TextTestRunner(verbosity=1).run(PARENT_SUITE)
