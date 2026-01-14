import base64


# Basic Authentication
def basic_auth(username, password):
    ascii_bytes = (username + ':' + password).encode('ascii', 'replace')
    basic_base64 = base64.b64encode(ascii_bytes).decode()
    auth = 'Basic ' + basic_base64

    return auth
