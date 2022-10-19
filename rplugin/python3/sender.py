import os
import socket
import tempfile

from pynvim import Nvim

SERVER = '127.0.0.1'
PORT = 5115
ADDRES = (SERVER, PORT)
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))


class Sender:
    def __init__(self, nvim: Nvim) -> None:
        ...


def send_buffer(nvim: Nvim) -> None:
    with tempfile.NamedTemporaryFile('w', delete=False) as temp_file:
        for line in nvim.current.buffer:
            temp_file.write(f'{line}\n')

    temp_file.close()
    _send_command(f'exec(open("{temp_file.name}").read())')

    if os.path.isfile(temp_file.name):
        os.remove(temp_file.name)


def send_selection(nvim: Nvim) -> None:
    with tempfile.NamedTemporaryFile('w', delete=False) as temp_file:
        commands = (
            ('call setreg("9", getreg("0"))'),
            ('normal! "0y'),
            (f'call writefile(getreg("0", 1, 1), "{temp_file.name}")'),
            ("call setreg('\"', getreg('9'))"),
        )

        for command in commands:
            nvim.command((command))

    temp_file.close()
    _send_command(f'exec(open("{temp_file.name}").read())')

    if os.path.isfile(temp_file.name):
        os.remove(temp_file.name)


def ensure_stream() -> None:
    command = (
        'import sys;'
        'sys.path.append("{0}") '
        'if "{0}" not in sys.path else 0;'
        'import streamer;'
        'streamer.start();'
    )

    _send_command(command.format(MODULE_PATH))


def stop_stream() -> None:
    _send_command('sreamer.stop()')


def _send_command(command, address=ADDRES) -> None:
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        connection.connect(address)
        connection.send(_format_command(command))
        connection.recv(4096)
        connection.close()
    except socket.error:
        ...


def _format_command(command) -> bytes:
    command = command.replace('"', '\\"')
    command = f'python("{command}")'
    return command.encode()
