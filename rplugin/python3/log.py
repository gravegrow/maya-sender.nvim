import os
import socket
import sys

PATH = os.path.dirname(os.path.abspath(__file__))
if PATH not in sys.path:
    sys.path.append(PATH)
    import sender

from config import COMMAND_ADDRESS, LOGGER_ADDRESS, MODULE_FILE, MODULE_PATH
from pynvim import Nvim


class Window:
    def __init__(self, nvim: Nvim) -> None:
        self.nvim = nvim
        self.buffer = None
        self.window = None

    @property
    def is_opened(self) -> bool:
        return self.window in self.nvim.windows

    def toggle(self) -> None:
        cur_win = self.nvim.current.window
        if self.window not in self.nvim.windows:
            self._create_terminal_window()

            if self.buffer not in self.nvim.buffers:
                self._create_terminal_buffer()

            self.nvim.api.win_set_buf(self.window, self.buffer)
            self.nvim.command("silent $")

        else:
            if len(self.nvim.windows) == 1:
                self.nvim.command("sbuffer")
            self._close_window()

        if cur_win == self.window or cur_win not in self.nvim.windows:
            return

        self.nvim.api.set_current_win(cur_win)

    def _close_window(self) -> None:
        self.nvim.api.win_close(self.window, True)
        self.window = None

    def _command_comp(self, commands=()) -> str:
        return "".join("{0}|".format(opt) for opt in commands).rstrip("|")

    def _create_terminal_window(self) -> None:
        commands = ("sbuffer", "resize 10")
        self.nvim.command(self._command_comp(commands))
        self.window = self.nvim.current.window

    def _create_terminal_buffer(self) -> None:
        command = "terminal python {0}".format(MODULE_FILE)
        post = (
            "setlocal winhighlight=Normal:MsgArea",
            "setlocal norelativenumber",
            "setlocal nonumber",
            "setlocal nobuflisted",
        )

        self.nvim.command(command)
        self.nvim.command(self._command_comp(post))
        self.buffer = self.nvim.current.buffer


def start_stream(address, streamer_address) -> None:
    command = (
        # fmt: off
        'import sys;'
        'sys.path.append("{0}") '
        'if "{0}" not in sys.path else 0;'
        'import streamer;'
        'streamer.start({1});'
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
