from .authorization import basic_auth
import requests
import xmltodict as xd

# Global variables
base_url = 'https://api.govdelivery.com/api/account/'
endpoint = '/bulletins'
endpoint_send = '/send_now'


def format_bulletin(subject, message, category_codes: list, topic_codes: list = None, optional_fields: dict = None):
    payload_subject = '<subject>' + subject + '</subject>'
    payload_message = '<body><![CDATA[' + message + ']]></body>'
    payload_categories = '<categories type="array">'
    body = '<bulletin>' + payload_subject + payload_message

    for category in category_codes:
        payload_categories = payload_categories + '<category><code>' + category + '</code></category>'
    payload_categories = payload_categories + '</categories>'

    if topic_codes:
        payload_topics = '<topics type="array">'
        for topic in topic_codes:
            payload_topics = payload_topics + '<topic><code>' + topic + '</code></topic>'
        payload_topics = payload_topics + '</topics>'
        body = body + payload_topics
    else:
        payload_topics = '<topics type="array"></topics>'
        body = body + payload_topics

    if optional_fields:
        for key in optional_fields:
            body = '<' + key + '>' + optional_fields[key] + '</' + key + '>'

    body = body + payload_categories + '</bulletin>'

    return body


def create_and_send_bulletin(username, password, account_code, body):
    auth = basic_auth(username, password)
    url = base_url + account_code + endpoint + endpoint_send
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


def get_bulletin(username, password, account_code, bulletin_id):
    auth = basic_auth(username, password)
    url = base_url + account_code + endpoint + '/' + bulletin_id + '.xml'
    headers = {'Content-Type': 'text/xml; charset: utf-8',
               'Authorization': auth}

    payload = requests.request('GET',
                               url,
                               headers=headers)
    try:
        payload.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)

    data = xd.parse(payload.content)

    return data
