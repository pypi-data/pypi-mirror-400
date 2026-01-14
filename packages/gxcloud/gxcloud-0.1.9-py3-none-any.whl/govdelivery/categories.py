from .authorization import basic_auth
import requests
import xmltodict as xd

# Global API variables
base_url = 'https://api.govdelivery.com/api/account/'
endpoint = '/categories.xml'
xml_attributes = {'default-open': ' type="boolean"'}
base_header = {'Content-Type': 'text/xml; charset: utf-8'}


# List Categories
def list_categories(username, password, account_code):
    auth = basic_auth(username, password)
    url = base_url + account_code + endpoint
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


# Create Category
def format_category(name, short_name, code, subscriptions=True, fields: dict = None):
    body = '<category><code>' + code + '</code><name>' + name + '</name><short-name>' + short_name + '</short-name>'

    if subscriptions:
        body = body + '<allow-subscriptions type="boolean">true</allow-subscriptions>'

    if fields:
        for key in fields:
            if key in xml_attributes.keys():
                body = body + '<' + key + xml_attributes[key] + '>' + fields[key] + '</' + key + '>'
            else:
                body = body + '<' + key + '>' + fields[key] + '</' + key + '>'
        body = body + '</category>'
    else:
        body = body + '</category>'

    return body


def create_category(username, password, account_code, body):
    auth = basic_auth(username, password)
    url = base_url + account_code + endpoint
    headers = base_header
    headers.update(Authorization=auth)

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


def update_category(username, password, account_code, category_code, body):
    auth = basic_auth(username, password)
    url = base_url + account_code + '/categories/' + category_code + '.xml'
    headers = base_header
    headers.update(Authorization=auth)

    payload = requests.request('PUT',
                               url,
                               data=body,
                               headers=headers)

    try:
        payload.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)

    data = xd.parse(payload.content)

    return data
