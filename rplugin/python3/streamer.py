import socket
from io import StringIO
from sys import version_info

from maya.api import OpenMaya as om

SERVER = '127.0.0.1'
PORT = 5116
BUFFER_SIZE = 8 * 1024
MAYA_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
PYTHON_VERSION = version_info.major


def start(address=(SERVER, PORT)):
    global CALLBACK
    CALLBACK = globals().get('CALLBACK')
    if CALLBACK is None:
        add_callback = om.MCommandMessage.addCommandOutputCallback
        CALLBACK = add_callback(_callback, address)


def stop():
    global CALLBACK
    om.MMessage.removeCallback(CALLBACK)
    CALLBACK = None


def _callback(message, mtype, address):
    output = StringIO()

    prefix = prefixes.get(mtype)
    if prefix is not None:
        message = '{0}{1}{2}'.format(prefix, message, Colors.clear)

    if PYTHON_VERSION == 2:
        message = message.decode('unicode-escape')  # pyright: ignore

    output.write(message.rstrip())
    output.seek(0)

    messages = output.read(int(BUFFER_SIZE))
    if not messages:
        output.close()
        return

    MAYA_CLIENT.sendto(messages.encode(), address)

    output.close()


class Colors:
    error = '\u001b[31m'
    warning = '\u001b[33m'
    result = '\u001b[32m'
    info = '\u001b[36m'
    stack = '\u001b[33m'
    clear = '\u001b[0m'


def prefix_format(color, msg):
    return '{0}{1}'.format(color, msg)


prefixes = {
    om.MCommandMessage.kError: prefix_format(Colors.error, 'ERROR: '),
    om.MCommandMessage.kWarning: prefix_format(Colors.warning, 'WARNING: '),
    om.MCommandMessage.kResult: prefix_format(Colors.result, 'RESULT: '),
    om.MCommandMessage.kStackTrace: prefix_format(Colors.stack, 'STACK: '),
    om.MCommandMessage.kInfo: Colors.info,
}


if __name__ == '__main__':
    start()