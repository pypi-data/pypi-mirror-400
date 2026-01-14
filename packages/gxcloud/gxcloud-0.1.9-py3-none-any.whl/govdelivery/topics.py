from .authorization import basic_auth
import requests
import xmltodict as xd

# Global API variables
base_url = 'https://api.govdelivery.com/api/account/'
topics_endpoint = '/topics.xml'
base_header = {'Content-Type': 'text/xml; charset: utf-8'}


# List Topics
def list_topics(username, password, account_code):
    auth = basic_auth(username, password)
    url = base_url + account_code + topics_endpoint
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


# Format a new topic.
def format_topic(name, short_name, category_codes: list = None, fields: dict = None):
    body = '<topic><name>' + name + '</name><short-name>' + short_name + '</short-name>'

    if category_codes:
        body = body + '<categories type="array">'
        for category in category_codes:
            body = body + '<category><code>' + category + '</code></category>'
        body = body + '</categories>'

    if fields:
        for key in fields:
            body = body + '<' + key + '>' + fields[key] + '</' + key + '>'

    body = body + '</topic>'

    return body


# Create a new topic.
def create_topic(username, password, account_code, body):
    auth = basic_auth(username, password)
    url = base_url + account_code + topics_endpoint
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
