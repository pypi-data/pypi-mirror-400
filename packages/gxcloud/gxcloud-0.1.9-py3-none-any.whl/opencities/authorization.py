import uuid
import hmac
import hashlib
import base64
import time
from urllib import parse
import json


# Function to authenticate the OC API using hmac.
def authorize(url, api_key, app_id, method='GET', body=''):
    method = method.upper()
    nonce = str(uuid.uuid4()).replace('-', '')[0:8]
    enc_url = parse.quote(url, safe='').lower()
    enc_body = str(base64.b64encode(bytes(json.dumps(body), 'utf-8')).decode())
    timestamp = str(int(time.time()))
    message = app_id + method + enc_url + timestamp + nonce

    if body != '':
        message = message + enc_body

    signature = base64.b64encode(hmac.new(bytes(api_key, 'utf-8'),
                                          bytes(message, 'utf-8'),
                                          digestmod=hashlib.sha256).digest()
                                 ).decode()

    auth = 'hmac ' + app_id + ':' + signature + ':' + nonce + ':' + timestamp

    return auth


def basic_auth(api_key, app_id):
    ascii_bytes = (app_id + ':' + api_key).encode('ascii', 'replace')
    basic_base64 = base64.b64encode(ascii_bytes).decode()
    auth = 'Basic ' + basic_base64

    return auth
