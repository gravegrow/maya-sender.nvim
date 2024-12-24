import os
import socket


PATH = os.path.dirname(os.path.abspath(__file__))


def send_file(file_path: str, project_path: str, address: tuple) -> None:
    reload_project_module(project_path, address)
    send_command(f'exec(open("{file_path}").read())', address)


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


def reload_project_module(project_path, address):
    send_command("import sys", address)
    send_command(
        f"if '{PATH}' not in sys.path:sys.path.append('{project_path}')",
        address,
    )
    send_command(f"import reloader; reloader.reload('{project_path}')", address)
    print("perfomed")
