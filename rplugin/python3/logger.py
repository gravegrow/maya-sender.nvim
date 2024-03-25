import os
import socket
import sys

import sender
from config import COMMAND_ADDRESS, LOGGER_ADDRESS, MODULE_PATH

PATH = os.path.dirname(os.path.abspath(__file__))
if PATH not in sys.path:
    sys.path.append(PATH)


def start_stream(address, streamer_address) -> None:
    command = (
        # fmt: off
        "import sys;"
        'sys.path.append("{0}") '
        'if "{0}" not in sys.path else 0;'
        "import utils.streamer as streamer;"
        "streamer.start({1});"
        # fmt: on
    )

    sender.send_command(command.format(MODULE_PATH, streamer_address), address)


def stop_stream(address) -> None:
    sender.send_command("streamer.stop()", address)


def keyboard_interrupt(function):
    def wrap(**kwargs):
        try:
            function(**kwargs)
        except KeyboardInterrupt:
            pass

    return wrap


@keyboard_interrupt
def listen() -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(LOGGER_ADDRESS)

    while True:
        data = server.recvfrom(1024)
        if not data:
            break
        message = data[0]
        print(message.decode())


if __name__ == "__main__":
    start_stream(COMMAND_ADDRESS, LOGGER_ADDRESS)
    listen()
