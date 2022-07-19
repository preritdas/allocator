class Alpaca:
    API_KEY = ''
    API_SECRET = ''
    BASE_URL = ''
    

class Nexmo:
    api_key = ''
    api_secret = ''
    sender: str = ''


class Gmail:
    smtp_host: str = 'smtp.gmail.com'
    smtp_port: int = 465
    email_address = '' 
    password = ''


class User:
    phone_number: str = ''
    email_address = ''
