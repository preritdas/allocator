# Non-local imports
import nexmo

# Local imports
import _keys

# Instantiate Nexmo client
nexmo_client = nexmo.Client(
    key = _keys.Nexmo.api_key,
    secret = _keys.Nexmo.api_secret
)

# Instantiate sms object
sms = nexmo.Sms(client = nexmo_client)

def text_me(*messages: str):
    """
    Concatenates all given arguments. Doesn't add spaces between them.
    Sends the message using the Nexmo account and user phone number
    given in the _keys.py module.
    
    Returns True if the first (usually only) message sent had successful
    delivery. Otherwise, returns False.
    """
    # Create the message

    text_content = ''
    for item in messages:
        text_content += item

    sms.send_message(
        {
            "from": _keys.Nexmo.sender,
            "to": _keys.User.phone_number,
            "text": text_content
        }
    )
