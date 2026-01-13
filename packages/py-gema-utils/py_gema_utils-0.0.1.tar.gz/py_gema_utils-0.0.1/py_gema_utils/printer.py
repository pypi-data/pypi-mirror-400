"""created as a test for the poetry and deployment
"""
from datetime import datetime


def print_z(message: str) -> None:
    """Prints the message and adds at the end of the message the current date
    """
    print(f"{message} %s" % datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"))
