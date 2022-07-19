# Non-local imports
import nexmo

# Local imports
import _keys
import smtplib  # emails
import ssl  # emails


# Instantiate Nexmo client
nexmo_client = nexmo.Client(
    key = _keys.Nexmo.api_key,
    secret = _keys.Nexmo.api_secret
)
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

    text_content = 'Message from Allocator: '
    for item in messages:
        text_content += item

    sms.send_message(
        {
            "from": _keys.Nexmo.sender,
            "to": _keys.User.phone_number,
            "text": text_content
        }
    )


def email_me(*messages: str, subject: str = "Message From Allocator") -> None:
    """
    Basic email framework is taken care of, including signature.
    Concatenates all args, like `text_me.` 
    `messages` can be generic text, or whatever is passed to `text_me` function.
    """
    # Unpack messages into a string
    messages = "".join(messages)

    content = (
        f"From: Allocator <{_keys.Gmail.email_address}>\n"
        f"To: {_keys.User.name.title()} <{_keys.User.email_address}>\n"
        f"Subject: {subject} \n\n"
        f"Dear {_keys.User.name.title()},\n\n"
        f"{messages} \n\n"
        "-Allocator"
    )

    context = ssl.create_default_context()
    
    with smtplib.SMTP_SSL(
        host=_keys.Gmail.smtp_host, 
        port=_keys.Gmail.smtp_port, 
        context=context
    ) as server:
        server.login(
            user = _keys.Gmail.email_address,
            password = _keys.Gmail.password
        )
        server.sendmail(
            from_addr = _keys.Gmail.email_address,
            to_addrs = _keys.User.email_address,
            msg = content
        )
