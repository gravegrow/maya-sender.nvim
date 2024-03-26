import socket
from io import StringIO

from maya.api import OpenMaya as om  # type: ignore

MAYA_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def start(address: tuple):
    global CALLBACK
    if globals().get("CALLBACK") is None:
        add_callback = om.MCommandMessage.addCommandOutputCallback
        CALLBACK = add_callback(callback, address)


def callback(message, mtype, address):
    output = StringIO()

    prefix = prefixes.get(mtype)
    if prefix is not None:
        message = "{0}{1}{2}".format(prefix, message, Colors.clear)

    output.write(message.rstrip())
    output.seek(0)

    messages = output.read(int(8192))
    if not messages:
        output.close()
        return

    MAYA_CLIENT.sendto(messages.encode(), address)

    output.close()


class Colors:
    error = "\u001b[31m"
    warning = "\u001b[33m"
    result = "\u001b[32m"
    info = "\u001b[36m"
    stack = "\u001b[33m"
    clear = "\u001b[0m"


def fmt(color, msg):
    return "{0}{1}".format(color, msg)


prefixes = {
    om.MCommandMessage.kError: fmt(Colors.error, "ERROR: "),
    om.MCommandMessage.kWarning: fmt(Colors.warning, "WARNING: "),
    om.MCommandMessage.kResult: fmt(Colors.result, "RESULT: "),
    om.MCommandMessage.kStackTrace: fmt(Colors.stack, "STACK: "),
    om.MCommandMessage.kInfo: Colors.info,
}


if __name__ == "__main__":
    SERVER = "127.0.0.1"
    PORT = 5116
    start((SERVER, PORT))
