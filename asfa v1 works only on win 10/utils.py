__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"


import os
import socket


def start_file(filename):
    """
        open file using the default app
    """
    try:
        os.startfile(filename)
    except Exception as e:
        print("[Error Opening File]", e)


def isPortAvailable(port):
    """
        test and see if a port number is free
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    return not (result == 0)


def delete_file(filename):
    """
        permanently delete a file
    """
    os.unlink(filename)
