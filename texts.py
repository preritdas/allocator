# Non-local imports
import nexmo

# Local imports
import _keys

# Instantiate Nexmo client
nexmo_client = nexmo.Client(
    key = _keys.nexmo_api_key,
    secret = _keys.nexmo_api_secret 
)

# Instantiate sms object
sms = nexmo.Sms(client = nexmo_client)

def text_me(*messages: str):
    # Create the message

    text_content = ''
    for item in messages:
        text_content += item

    text_response = sms.send_message(
        {
            "from": _keys.nexmo_sender,
            "to": _keys.nexmo_my_number,
            "text": text_content
        }
    )
    return True if text_response["messages"][0]["status"] == '0' else False