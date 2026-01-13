import re

def strip_ansi_codes(text: str) -> str:
    """
    Removes ANSI escape sequences (colors, bold text) often used by CLI tools.
    This ensures the output we capture is clean text.
    """
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)

