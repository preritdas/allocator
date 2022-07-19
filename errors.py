"""Report errors to user."""


# Project modules
import texts


def report_error(error: str) -> None:
    content = "Error reported: " + error
    texts.text_me(content)
