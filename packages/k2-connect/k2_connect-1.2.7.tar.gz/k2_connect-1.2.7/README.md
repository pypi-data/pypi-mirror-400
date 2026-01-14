# k2-connect-python
[![PyPI](https://img.shields.io/pypi/v/k2-connect?style=for-the-badge)](https://pypi.org/project/k2-connect/)

k2-connect is a Python library for accessing the Kopo Kopo APIs.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install k2connect.

```bash
pip3 install k2-connect
```

## Usage
### Initialization
The library is initialized once then all services maybe accessed by creating different instances for specific services.
The `BASE_URL` is a custom value and any url maybe passed provided it is secured and should only be accessible over TLS (HTTPS) and your server should have a valid certificate.
Initialization requires the following arguments:
* `base_url`
* `client_id`
* `client_secret`

```python
import os
import k2connect

CLIENT_ID = 'my_client_id'
CLIENT_SECRET = os.getenv('MY_CLIENT_SECRET')
BASE_URL = 'https://sandbox.kopokopo.com/'

#initialize the library
k2connect.initialize(CLIENT_ID, CLIENT_SECRET, BASE_URL)
```

### k2connect services
After initialization, k2connect services may be accessed by creating instances of a specific service. For instance:
```python
# create an instance of the service 
authenticator = k2connect.Tokens

# access a method provided by the service
authenticator.request_access_token()
```
One can access the following k2connect services:
- [TokensService](#token-service)
- [PayService](#pay-service)
- [ReceivePaymentsService](#receive-payments-service)
- [TransferService](#transfers-service)
- [WebhookService](#webhook-service)
- [NotificationService](#notification-service)
- [PollingService](#polling-service)

#### Token service
The token service allows you to request access tokens that you will use in order to communicate with the Kopo Kopo APIs.
The token service avails the option for you to implement token refresh mechanism by providing the duration within which
the token will expire.

The `get_access_token()` and `get_token_expiry_duration()` methods each take a response object from which they extract the
token and expiry duration values.A request token and expiry duration time can be gotten as follows: 

```python
# create an instance of the token service
token_service = k2connect.Tokens

# request the access token
access_token_request = token_service.request_access_token()

# get access token
access_token = token_service.get_access_token(access_token_request)

# get expiry duration
token_expiry_duration = token_service.get_token_expiry_duration(access_token_request)
```

#### Pay service
The pay service enables you to add external entities (recipients) as destinations for payments made withe the pay service. 
It also enables you to make payments and check for a payment's status.


To add pay recipients the `add_pay_recipient()` method is used. The currently supported recipient types are `bank_account` and 
`mobile_wallet` the method then takes a set of key worded arguments required to create a recipient of either type. The accepted 
key worded arguments are as follows:

For `bank_account` recipient:  
* account_name `REQUIRED`
* account_number `REQUIRED`
* bank_branch_ref `REQUIRED`
* settlement_method `REQUIRED`


For `mobile_wallet` recipient:
* first_name `REQUIRED`
* last_name `REQUIRED`
* phone `REQUIRED`
* email `REQUIRED`
* network `REQUIRED`


For `till` recipient:
* till_name `REQUIRED`
* till_number `REQUIRED`


For `paybill` recipient:
* paybill_name `REQUIRED`
* paybill_number `REQUIRED`
* paybill_account_number `REQUIRED`

To send payments the `send_pay()` method is used. It takes the following arguments:
* bearer_token `REQUIRED`
* callback_url `REQUIRED`
* destination `REQUIRED`
* amount `REQUIRED`
* description `REQUIRED`
* currency='KES' `REQUIRED`
* metadata `OPTIONAL`. Maximum 5 dictionaries/hashes/key-value pairs.

 
Note: the currency argument is set to `KES` as the default currency since that is the only ISO currency currently supported. It may however, 
be overridden by passing a different currency value in its place. If you do not wish to override the `KES` currency you can simply avoid 
passing it as an argument.

The pay service also enables you to check the status of a transaction by querying a URL that points to the transaction resource, using the 
`pay_transaction_status()`.


 The Resource Location URL is returned by the either of the methods.

 ```python
# create an instance of the pay service
pay_service = k2connect.Pay

# create bank account pay recipient
bank_recipient_request = {
    "access_token": 'ACCESS_TOKEN',
    "recipient_type": 'bank_account',
    "settlement_method": "EFT",
    "account_name": "bank_account_name",
    "bank_branch_ref": "633aa26c-7b7c-4091-ae28-96c0687cf886",
    "account_number": "bank_account_number"
}
bank_pay_location = pay_service.add_pay_recipient(bank_recipient_request)

# create mobile wallet pay recipient
mobile_recipient_request = {
    "access_token": 'ACCESS_TOKEN',
    "recipient_type": 'mobile_wallet',
    "first_name": "mobile_wallet_first_name",
    "last_name": "mobile_wallet_last_name",
    "phone_number": "+254123456789",
    "network": "mobile_wallet_network",
    "email": "test@test.com"
}
mobile_pay_location = pay_service.add_pay_recipient(mobile_recipient_request)

# create till pay recipient
till_recipient_request = {
    "access_token": "ACCESS_TOKEN",
    "recipient_type": "till",
    "till_name": "till_name",
    "till_number": "till_number",
}
till_pay_location = pay_service.add_pay_recipient(till_recipient_request)

# create paybill pay recipient
paybill_recipient_request = {
    "access_token": "ACCESS_TOKEN",
    "recipient_type": "paybill",
    "paybill_name": "paybill_name",
    "paybill_number": "paybill_number",
    "paybill_account_number": "account_number",
}
paybill_pay_location = pay_service.add_pay_recipient(paybill_recipient_request)
                                                                
# send pay transaction to mobile wallet
request_payload = {
            "access_token": 'ACCESS_TOKEN',
            "destination_reference": '9764ef5f-fcd6-42c1-bbff-de280becc64b',
            "destination_type": 'mobile_wallet',
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "amount": '10',
            "currency": 'KES',
            "metadata": { "hey": 'there', "mister": 'angelo'}
        }
create_mobile_pay_location = pay_service.send_pay(request_payload)
                                                                
# send pay transaction to bank account
request_payload = {
            "access_token": 'ACCESS_TOKEN',
            "destination_reference": '9764ef5f-fcd6-42c1-bbff-de280becc64b',
            "destination_type": 'bank_account',
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "amount": '10',
            "currency": 'KES',
            "metadata": { "hey": 'there', "mister": 'angelo'}
        }
create_bank_pay_location = pay_service.send_pay(request_payload)
                                                                
# send pay transaction to till
request_payload = {
            "access_token": 'ACCESS_TOKEN',
            "destination_reference": '9764ef5f-fcd6-42c1-bbff-de280becc64b',
            "destination_type": 'till',
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "amount": '10',
            "currency": 'KES',
            "metadata": { "hey": 'there', "mister": 'angelo'}
        }
create_till_pay_location = pay_service.send_pay(request_payload)
                                                                
# send pay transaction to paybill account
request_payload = {
            "access_token": 'ACCESS_TOKEN',
            "destination_reference": '9764ef5f-fcd6-42c1-bbff-de280becc64b',
            "destination_type": 'paybill',
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "amount": '10',
            "currency": 'KES',
            "metadata": { "hey": 'there', "mister": 'angelo'}
        }
create_paybill_pay_location = pay_service.send_pay(request_payload)

# get payment request status
pay_request_status = pay_service.pay_transaction_status(access_token, create_mobile_pay_location)
```

#### Receive payments service
The receive payments service allows you to create requests for incoming payments over a specific channel and receive the payments 
to your account. You can also check the status of your payment requests and access the payment request through a URL.


In order to create a payment request, the `create_payment_request()` method is used. This method can be passed the following arguments:
* bearer_token `REQUIRED`
* callback_url `REQUIRED`
* first_name `REQUIRED`
* last_name `REQUIRED`
* payment_channel `REQUIRED`
* phone `REQUIRED`
* till_number `REQUIRED`
* value `REQUIRED`
* currency='KES' `REQUIRED`
* metadata `OPTIONAL`. Maximum 5 dictionaries/hashes/key-value pairs.

Note: the currency argument is set to `KES` as the default currency since that is the only ISO currency currently supported. It may however, 
be overridden by passing a different currency value in its place. If you do not wish to override the `KES` currency you can simply avoid 
passing it as an argument.


The method also creates the provision for optional `email` information to be passed in the key worded argument form, 
for instance:

`email='mycool@email.domain'`

Furthermore, the `create_payment_request()` allows you to add metadata information passed in the form of a maximum of 5 key worded arguments.  
The URL required for checking a payment request status is returned by default with the `create_payment_request` method.  

```python
import os

# get the access token
BEARER_TOKEN = os.getenv('MY_BEARER_TOKEN')

# create an instance of the receive payments service
receive_payments_service = k2connect.ReceivePayments

# create a payment request
request_payload = {
    "access_token": 'ACCESS_TOKEN',
    "callback_url": "https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d",
    "first_name": "python_first_name",
    "last_name": "python_last_name",
    "email": "daivd.j.kariuki@gmail.com",
    "payment_channel": "MPESA",
    "phone_number": "+254911222536",
    "till_number": "K112233",
    "amount": "10",
    "metadata": { "hey": 'there', "mister": 'angelo'}
}
mpesa_payment_location = receive_payments_service.create_payment_request(request_payload)

# get payment request status
payment_request_status = receive_payments_service.payment_request_status(access_token, mpesa_payment_location)
```

#### Transfers service
The transfer service enables you to create verified settlement mobile and bank accounts with respective `add_settlement_account()` methods. The method takes the following arguments:

Common for both:
* bearer_token `REQUIRED`

For `add_bank_settlement_account`:  
* account_name `REQUIRED`
* account_number `REQUIRED`
* bank_id `REQUIRED`
* bank_branch_id `REQUIRED`

For `add_mobile_wallet_settlement_account` recipient:  
* msisdn `REQUIRED`
* network: 'Safaricom' `REQUIRED`


The transfer service enables you to transfer funds to these pre-approved settlement accounts. To settle funds the `settle_funds()` is used. It enables you to make two types of transfer
transactions, a blind settlement and a targeted settlement. A blind transaction is made with the `destination` argument set to `None`, in the event that an ID for the destination of funds 
is provided then a targeted transfer is made to that destination. The method takes the following arguments:

* bearer_token `REQUIRED`
* transfer_value `REQUIRED`
* transfer_currency = 'KES' `REQUIRED`
* destination_type `OPTIONAL`
* destination_reference `OPTIONAL`  

Note: the currency argument is set to `KES` as the default currency since that is the only ISO currency currently supported. It may however, 
be overridden by passing a different currency value in its place. If you do not wish to override the `KES` currency you can simply avoid 
passing it as an argument.


You can check a transfer transaction's status by querying the transaction resource's location 
URL which is returned by the `settle_funds` method by default.  
The `transfer_transaction_status()` method is then used to check a transfer transaction status.

```python
# initialize the transfer service
transfer_service = k2connect.Transfers

# create verified settlement bank account
request_payload = {
            "access_token": 'ACCESS_TOKEN',
            "settlement_method": 'RTS',
            "account_name": 'py_sdk_account_name',
            "account_number": 'py_sdk_account_number',
            "bank_branch_ref": '633aa26c-7b7c-4091-ae28-96c0687cf886'
        }
settlement_account = transfer_service.add_bank_settlement_account(request_payload)
# create verified settlement mobile account
request_payload = {
    "access_token": 'ACCESS_TOKEN',
    "first_name": 'py_sdk_first_name',
    "last_name": 'py_sdk_last_name',
    "phone_number": '+254911222538',
    "network": 'Safaricom'
    }
settlement_account = transfer_service.add_mobile_wallet_settlement_account(request_payload)

# settle funds (blind transfer)
request_payload = {
    "access_token": 'ACCESS_TOKEN',
    "callback_url": 'url',
    "value": '10',
    }
transfer_transaction = transfer_service.settle_funds(request_payload) 

# settle funds (targeted transfer to a merchant_wallet)
request_payload = {
            "access_token": 'ACCESS_TOKEN',
            "destination_type": 'merchant_bank_account',
            "destination_reference": '87bbfdcf-fb59-4d8e-b039-b85b97015a7e',
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "value": '10',
        }
transfer_transaction_mobile_location = transfer_service.settle_funds(request_payload)

# settle funds (targeted transfer to a merchant_wallet)
request_payload = {
            "access_token": 'ACCESS_TOKEN',
            "destination_type": 'merchant_wallet',
            "destination_reference": 'eba238ae-e03f-46f6-aed5-db357fb00f9c',
            "callback_url": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
            "value": '10',
        }
transfer_transaction_bank_location = transfer_service.settle_funds(request_payload)

# get transfer transaction status
transfer_transaction_status = transfer_service.transfer_transaction_status(access_token, transfer_transaction_mobile_location or transfer_transaction_bank_location)
```

##### The destination_reference number corresponding to a settlement account must exist before you can settle_funds to it. 

#### Webhook service
The webhook service allows you to create subscriptions to events that occur on the KopoKopo application. The `create_subscription()` method is used, 
it takes the following arguments:

* bearer_token `REQUIRED`
* event_type `REQUIRED`
* webhook_endpoint `REQUIRED`
* client_secret `REQUIRED`


Currently the following events are supported:
* b2b_transaction_received
* buygoods_transaction_received
* buygoods_transaction_reversed
* m2m_transaction_received
* settlement_transfer_completed
* customer_created

```python
import os

# initialize service
webhook_service = k2connect.Webhooks

request_payload = {
    "access_token": 'ACCESS_TOKEN',
    "event_type": 'buygoods_transaction_received',
    "webhook_endpoint": 'https://webhook.site/52fd1913-778e-4ee1-bdc4-74517abb758d',
    "scope": 'till',
    "scope_reference": '112233'
    }

# create webhook subscription
customer_created_subscription = webhook_service.create_subscription(request_payload)
```

#### Notification service
This service allows you to send custom sms messages to successful buy-goods transactions received that occurred on the Kopo Kopo. 
It takes the following arguments:

* bearer_token `REQUIRED`
* webhookEventReference: The webhook event reference for a buygoods_transaction_received webhook. `REQUIRED`
* message: The message to be sent `REQUIRED`
* callbackUrl: Url that the result will be posted to `REQUIRED`

Note: A buygoods_transaction_received webhook subscription must have been created, with its subsequent webhook event in place.


You can check an SMS notification request's status by querying the requests' location 
URL which is returned by the `send_transaction_sms_notification` method by default.  
The `transaction_notification_status()` method is used to check an SMS notification request status.

```python
import os

# initialize notification service
notification_service = k2connect.Notifications

# create transaction sms notifications
request_payload = {
    "access_token": 'ACCESS_TOKEN',
    "callback_url": 'callback_url',
    "webhook_event_reference": "d81312b9-4c0e-4347-971f-c3d5b14bdbe4",
    "message": 'Alleluia',
    }
notification_resource_location_url = notification_service.send_transaction_sms_notification(request_payload)

# get request status
request_status = notification_service.transaction_notification_status(access_token, notification_resource_location_url)
```

#### Polling service
This service allows you to poll transactions received on the Kopo Kopo system within a certain time range, and either a company or a specific till. 
It takes the following arguments:

* bearer_token `REQUIRED`
* fromTime: The starting time of the polling request `REQUIRED`
* toTime: The end time of the polling request `REQUIRED`
* scope: The scope of the polling request `REQUIRED`
* scopeReference: The scope reference `REQUIRED for the 'till' scope`
* callbackUrl: Url that the result will be posted to `REQUIRED`

You can check a polling request's status by querying the requests' location 
URL which is returned by the `create_polling_request` method by default.  
The `polling_request_status()` method is used to check an polling request status.

```python
import os

# initialize service
notification_service = k2connect.Polling

# create polling request
request_payload = {
    "access_token": 'ACCESS_TOKEN',
    "callback_url": 'callback_url',
    "scope": "till",
    "scope_reference": "112233",
    "from_time": "2021-07-09T08:50:22+03:00",
    "to_time": "2021-07-10T18:00:22+03:00",
    }
polling_resource_location_url = notification_service.send_transaction_sms_notification(request_payload)

# get request status
request_status = notification_service.transaction_notification_status(access_token, polling_resource_location_url)
```

For more information, please read [Transaction Notification Docs](https://api-docs.kopokopo.com/#transaction-sms-notifications)

#### Result processor 
Results (inclusive of webhook results and results posted to callback URLs asynchronously) sent from KopoKopo have to be processed before payloads can 
be accessed. The result processor can be used to accomplish this using the `process()` method.

```python
# initialize result handler
result_handler = k2connect.ResultHandler

# process result 
processed_payload = result_handler.process(some_result)
```

#### Payload decomposer
Once a result is processed an a payload has been returned, it can be decomposed into its constituent result data using the payload decomposer.
The payload decomposer achieves this using the `decompose()` method.

```python
from k2connect import payload_decomposer

# decompose a payload
decomposer = payload_decomposer.decompose(processed_payload)

# get first name
first_name = decomposer.first_name
```

### Author
This library was written by [PhilipWafula](https://github.com/PhilipWafula) and [David Kariuki Mwangi](https://github.com/DavidJonKariz).

### Contributing
Bug reports and pull requests are welcome. Feel free raise issues on our [issues tracker](https://github.com/kopokopo/k2-connect-python/issues)

### License
k2connect-python is [MIT](https://github.com/kopokopo/k2-connect-python/blob/master/LICENSE) Licensed.

### Changelog
