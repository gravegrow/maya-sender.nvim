import os
import socket
import tempfile

from pynvim import Nvim


def send_buffer(nvim: Nvim, address: tuple) -> None:
    file = nvim.command_output('echo expand("%:p")')
    send_command(f'exec(open("{file}").read())', address)


def send_selection(nvim: Nvim, address) -> None:
    with tempfile.NamedTemporaryFile("w", delete=False) as temp_file:
        commands = (
            ('call setreg("9", getreg("0"))'),
            ('normal! "0y'),
            (f'call writefile(getreg("0", 1, 1), "{temp_file.name}")'),
            ("call setreg('\"', getreg('9'))"),
        )

        for command in commands:
            nvim.command((command))

    temp_file.close()
    send_command(f'exec(open("{temp_file.name}").read())', address)

    if os.path.isfile(temp_file.name):
        os.remove(temp_file.name)


def send_command(command, address) -> None:
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
