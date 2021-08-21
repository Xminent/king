from typing import Union


class NoMessageTypeError(Exception):
    """Class used to represent not providing a message type."""

    def __init__(self, message) -> None:
        super().__init__(colorify("ERROR", message))


class Color:
    BLACK = '\u001b[30m'
    RED = '\u001b[91m'
    GREEN = '\u001b[92m'
    YELLOW = '\u001b[93m'
    BLUE = '\u001b[94m'
    MAGENTA = '\u001b[95m'
    CYAN = '\u001b[96m'
    WHITE = '\u001b[37m'
    UNDERLINE = '\u001b[4m'
    RESET = '\u001b[0m'

    """Custom class for defining escape codes for colored terminal output."""
    def black(x): return Color.BLACK + str(x)
    def red(x): return Color.RED + str(x)
    def green(x): return Color.GREEN + str(x)
    def yellow(x): return Color.YELLOW + str(x)
    def blue(x): return Color.BLUE + str(x)
    def magenta(x): return Color.MAGENTA + str(x)
    def cyan(x): return Color.CYAN + str(x)
    def white(x): return Color.WHITE + str(x)
    def underline(x): return Color.UNDERLINE + str(x)
    def reset(x): return Color.RESET + str(x)


def printer(msg_type: str, msg: Union[int, str, float]) -> None:
    """Printing method for specific types of messages.

    Args:
        msg_type (str): Type of message to send. Options are:
        - INFO: yellow 
        - ERROR: red
        - BANNER: cyan
        - DEBUG: magenta
        - SUCCESS: green

        msg (str): The message to send.

    Raises:
        NoMessageTypeError: Raised when no message type was provided.
    """

    if msg_type == "INFO":
        return print(Color.yellow("[INFO!] : " + str(msg)) + Color.reset(" "))
    elif msg_type == "ERROR":
        return print(Color.red("[ERROR!] : " + str(msg)) + Color.reset(" "))
    elif msg_type == "BANNER":
        return print(Color.cyan(str(msg)) + Color.reset(" "))
    elif msg_type == "DEBUG":
        return print(Color.magenta("[DEBUG!] : " + str(msg)) + Color.reset(" "))
    elif msg_type == "DATA":
        return print(Color.blue("[DATA!] : " + str(msg)) + Color.reset(" "))
    elif msg_type == "SUCCESS":
        return print(Color.green("[SUCCESS!] : " + str(msg)) + Color.reset(" "))

    raise NoMessageTypeError("No message type was provided.")


def colorify(msg_type: str, msg: Union[int, str, float]) -> str:
    """Returns colored text for use anywhere needed,

    Args:
        msg_type (str): Type of message to send. Options are:
        - INFO: yellow 
        - ERROR: red
        - BANNER: cyan
        - DEBUG: magenta
        - SUCCESS: green

        msg (Union[int, str, float]): The message to send.

    Raises:
        NoMessageTypeError: Raised when no message type was provided.

    Returns:
        str: Colored string.
    """
    if msg_type == "INFO":
        return(Color.yellow("[INFO!] : " + str(msg)) + Color.reset(" "))
    elif msg_type == "ERROR":
        return(Color.red("[ERROR!] : " + str(msg)) + Color.reset(" "))
    elif msg_type == "BANNER":
        return(Color.cyan(str(msg)) + Color.reset(" "))
    elif msg_type == "DEBUG":
        return(Color.magenta("[DEBUG!] : " + str(msg)) + Color.reset(" "))
    elif msg_type == "DATA":
        return(Color.blue("[DATA!] : " + str(msg)) + Color.reset(" "))
    elif msg_type == "SUCCESS":
        return(Color.green("[SUCCESS!] : " + str(msg)) + Color.reset(" "))

    raise NoMessageTypeError("No message type was provided.")
