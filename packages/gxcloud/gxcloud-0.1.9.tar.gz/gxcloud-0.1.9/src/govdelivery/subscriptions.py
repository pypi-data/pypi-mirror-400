from .authorization import basic_auth
import requests
import xmltodict as xd
import base64

# Global variables
base_url = 'https://api.govdelivery.com/api/account/'
endpoint_subscriber = '/subscribers.xml'
endpoint_categories = '/categories.xml'
base_header = {'Content-Type': 'text/xml; charset: utf-8'}


def encode_email_subscriber(email):
    ascii_bytes = email.encode('ascii', 'replace')
    basic_base64 = base64.b64encode(ascii_bytes).decode()

    return basic_base64


def format_email_subscriber(email, notifications=False, digest=0):
    body = '<subscriber><email>' + email + '</email>'
    if notifications:
        body = body + '<send-notifications type="boolean">true</send-notifications>'
    else:
        body = body + '<send-notifications type="boolean">false</send-notifications>'
    body = body + '<digest-for>' + str(digest) + '</digest-for>'
    body = body + '</subscriber>'

    return body


def list_category_subscriptions(username, password, account_code, email):
    auth = basic_auth(username, password)
    subscriber_id = encode_email_subscriber(email)
    url = base_url + account_code + '/subscribers/' + subscriber_id + '/categories.xml'
    headers = base_header
    headers.update(Authorization=auth)

    payload = requests.request('GET',
                               url,
                               headers=headers)
    try:
        payload.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)

    data = xd.parse(payload.content)

    return data


def create_email_subscriber(account_code, username, password, body):
    url = base_url + account_code + endpoint_subscriber
    auth = basic_auth(username, password)
    headers = {'Content-Type': 'text/xml; charset: utf-8',
               'Authorization': auth}

    payload = requests.request('POST',
                               url,
                               data=body,
                               headers=headers)

    try:
        payload.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)

    data = xd.parse(payload.content)

    return data


def format_category_subscriptions(categories: list, notifications=False):
    body = '<subscriber>'
    if notifications:
        body = body + '<send-notifications type="boolean">true</send-notifications>'
    else:
        body = body + '<send-notifications type="boolean">false</send-notifications>'
    body = body + '<categories type="array">'
    for category in categories:
        body = body + '<category><code>' + category + '</code></category>'
    body = body + '</categories>'
    body = body + '</subscriber>'

    return body


def change_category_subscriptions(account_code, username, password, subscriber, body):
    url = base_url + account_code + '/subscribers/' + subscriber + '/' + endpoint_categories
    auth = basic_auth(username, password)
    headers = {'Content-Type': 'text/xml; charset: utf-8',
               'Authorization': auth}

    payload = requests.request('PUT',
                               url,
                               data=body,
                               headers=headers)

    try:
        payload.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)

    data = 'Category subscriptions updated successfully.'

    return data
