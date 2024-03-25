import sys

from pynvim import Nvim, command, plugin


import sender
from config import COMMAND_ADDRESS, PATH

if PATH not in sys.path:
    sys.path.append(PATH)


@plugin
class MayaSender:
    def __init__(self, nvim: Nvim):
        self.nvim = nvim

    @command("MayaSendSelection")
    def send_selection(self):
        self._reload()
        sender.send_selection(self.nvim, COMMAND_ADDRESS)

    @command("MayaSendBuffer")
    def send_buffer(self):
        self._reload()
        sender.send_buffer(self.nvim, COMMAND_ADDRESS)

    def _reload(self):
        sender.send_command(
            f'exec(open("{PATH + "/reloader.py"}").read())',
            COMMAND_ADDRESS,
        )

        cwd = self.nvim.command_output("pwd")
        sender.send_command(
            f"import reloader; reloader.reload('{cwd}')",
            COMMAND_ADDRESS,
        )
