"""
Report errors to user by text. 
"""
# External
from rich.console import Console # type hints

# Project modules
import delivery


def report_error(error: str, console: Console = None) -> None:
    """
    Report an error by text message and optionally log it to console.

    Console logging occurs only if a Rich console object is passed in.
    """
    content = "Error reported: " + error
    delivery.text_me(content)

    if console and isinstance(console, Console): 
        console.log(f"Error: {error}")
