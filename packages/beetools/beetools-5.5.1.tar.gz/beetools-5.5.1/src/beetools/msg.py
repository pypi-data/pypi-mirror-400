from termcolor import colored

# Message defaults
BAR_LEN = 50
MSG_LEN = 50
CRASH_RETRY = 2


def display(p_msg, p_len=MSG_LEN, p_color="white") -> str:
    """Return a text message in white on black.

    Parameters
    ----------
    p_msg
        The message
    p_len
        The fixed length of the message. Default is beetools.MSG_LEN
    p_color
        Color of the text, always on black.
            [ Grey, red, green, yellow, blue, magenta, cyan, white ]

    Returns
    -------
    str
        Text in the specified color.

    Examples
    --------
    >>> from beetools.msg import display
    >>> display('Display message')
    '\\x1b[37mDisplay message                               '

    """
    msg = colored("{: <{len}}".format(p_msg, len=p_len), p_color)
    return msg[:p_len] + " "


def error(p_msg) -> str:
    """Return an "error" text message in red on black

    Parameters
    ----------
    p_msg
        The message

    Returns
    -------
    str
        Text in red on black.

    Examples
    --------
    >>> from beetools.msg import error
    >>> error( 'Error message' )
    '\\x1b[31mError message\\x1b[0m'

    """
    return colored(f"{p_msg}", "red")


def header(p_msg) -> str:
    """Return a "header" text message in cyan on black

    Parameters
    ----------
    p_msg
        The message

    Returns
    -------
    str
        Text in red on black.

    Examples
    --------
    >>> from beetools.msg import header
    >>> header('Header message')
    '\\x1b[36mHeader message\\x1b[0m'

    """
    return colored(f"{p_msg}", "cyan")


def info(p_msg) -> str:
    """Return an "information" text message in yellow on black

    Parameters
    ----------
    p_msg
        The message

    Returns
    -------
    str
        Text in red on black.

    Examples
    --------
    >>> from beetools.msg import info
    >>> info('Info message')
    '\\x1b[33mInfo message\\x1b[0m'

    """
    return colored(f"{p_msg}", "yellow")


def milestone(p_msg) -> str:
    """Return a "milestone" text message in magenta on black

    Parameters
    ----------
    p_msg
        The message

    Returns
    -------
    str
        Text in red on black.

    Examples
    --------
    >>> from beetools.msg import milestone
    >>> milestone('Milestone message')
    '\\x1b[35mMilestone message\\x1b[0m'

    """
    return colored(f"{p_msg}", "magenta")


def ok(p_msg) -> str:
    """Return an "OK" text message in green on black

    Parameters
    ----------
    p_msg
        The message

    Returns
    -------
    str
        Text in red on black.

    Examples
    --------
    >>> from beetools.msg import ok
    >>> ok('OK message')
    '\\x1b[32mOK message\\x1b[0m'

    """
    return colored(f"{p_msg}", "green")


def example_messaging():
    """Standard example to illustrate standard use.

    Parameters
    ----------

    Returns
    -------
    bool
        Successful execution [ b_tls.archive_path | False ]

    Examples
    --------

    """
    success = True
    print(
        display(
            f"This message print in blue and cut at {MSG_LEN} character because it is too long!",
            p_color="blue",
        )
    )
    print(ok("This message is an OK message"))
    print(info("This is an info message"))
    print(milestone("This is a milestone message"))
    print(error("This is a warning message"))
    return success


def do_examples():
    return example_messaging()


if __name__ == "__main__":
    do_examples()
