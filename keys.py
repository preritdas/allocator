import configparser


keys = configparser.ConfigParser()
keys.read('keys.ini')


class Alpaca:
    _keys = keys['Alpaca']

    API_KEY = _keys['api_key']
    API_SECRET = _keys['api_secret']
    BASE_URL = _keys['base_url']
    

class Nexmo:
    _keys = keys['Nexmo']

    api_key = _keys['api_key']
    api_secret = _keys['api_secret']
    sender = _keys['sender']


class Gmail:
    _keys = keys['Gmail']

    smtp_host = _keys['smtp_host']
    smtp_port = int(_keys['smtp_port'])
    email_address = _keys['email_address']
    password = _keys['password']


class User:
    _keys = keys['User']

    name = _keys['name']
    phone_number = _keys['phone_number']
    email_address = _keys['email_address']
