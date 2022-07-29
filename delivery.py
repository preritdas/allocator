# Non-local imports
import nexmo

# Local imports
import keys
import smtplib  # emails
import ssl  # emails

# Project modules
from config import Config


# Instantiate Nexmo client
nexmo_client = nexmo.Client(
    key = keys.Nexmo.api_key,
    secret = keys.Nexmo.api_secret
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
            "from": keys.Nexmo.sender,
            "to": keys.User.phone_number,
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
        f"From: Allocator <{keys.Gmail.email_address}>\n"
        f"To: {keys.User.name.title()} <{keys.User.email_address}>\n"
        f"Subject: {subject} \n\n"
        f"Dear {keys.User.name.title()},\n\n"
        f"{messages} \n\n"
        "-Allocator"
    )

    context = ssl.create_default_context()
    
    with smtplib.SMTP_SSL(
        host = keys.Gmail.smtp_host, 
        port = keys.Gmail.smtp_port, 
        context = context
    ) as server:
        server.login(
            user = keys.Gmail.email_address,
            password = keys.Gmail.password
        )
        server.sendmail(
            from_addr = keys.Gmail.email_address,
            to_addrs = Config.email_recipients,
            msg = content
        )
