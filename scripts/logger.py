import os
import socket
import sender

PATH = os.path.dirname(os.path.abspath(__file__))
SENDER_ADDRESS = ("localhost", 5115)
LOGGER_ADDRESS = ("localhost", 5116)


def start_stream(host_address, logger_address) -> None:
    command = (
        # fmt: off
        "import sys;"
        'sys.path.append("{0}") '
        'if "{0}" not in sys.path else 0;'
        "import streamer as streamer;"
        "streamer.start({1});"
        # fmt: on
    )

    sender.send_command(command.format(PATH, logger_address), host_address)


def stop_stream(sender_address) -> None:
    sender.send_command("streamer.stop()", sender_address)


def keyboard_interrupt(function):
    def wrap(*args, **kwargs):
        try:
            function(*args, **kwargs)
        except KeyboardInterrupt:
            pass

    return wrap


@keyboard_interrupt
def listen(logger_address) -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(logger_address)

    while True:
        data = server.recvfrom(1024)
        if not data:
            break
        message = data[0]
        print(message.decode())


if __name__ == "__main__":
    start_stream(SENDER_ADDRESS, LOGGER_ADDRESS)
    listen(LOGGER_ADDRESS)
