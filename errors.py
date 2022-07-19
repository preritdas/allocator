"""Report errors to user."""


# Project modules
import delivery


def report_error(error: str) -> None:
    content = "Error reported: " + error
    delivery.text_me(content)
