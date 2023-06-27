import os
import sys

import pynvim
from pynvim import Nvim, command, plugin

PATH = os.path.dirname(os.path.abspath(__file__))
DEVKIT = (
    "/media/storage/dev/maya/devkitBase/devkit/other/Python27/pymel/extras/completion/py/"
)

sys.path.append(DEVKIT)

if PATH not in sys.path:
    sys.path.append(PATH)

    import log
    import sender
    from config import COMMAND_ADDRESS, PATH


@plugin
class MayaSender:
    def __init__(self, nvim: Nvim):
        self.nvim = nvim
        self.log_window = log.Window(nvim)

    @command("MayaSendSelection", sync=True)
    def send_selection(self):
        sender.send_selection(self.nvim, COMMAND_ADDRESS)

    @command("MayaSendBuffer", sync=True)
    def send_buffer(self):
        sender.send_buffer(self.nvim, COMMAND_ADDRESS)

    # @command("MayaOpenLog", sync=True)
    # def toggle_log_widnow(self):
    #     self.log_window.toggle()
    #     if self.log_window.is_opened:
    #         self._ensure_stream()

    # @command("MayaConnect", sync=True)
    # def start_stream(self):
    #     self._ensure_stream()
    #
    # @command("MayaDisconnect", sync=True)
    # def stop_stream(self):
    #     sender.stop_stream(ADDRESS)

    # def _ensure_stream(self):
    #     sender.ensure_stream(ADDRESS, (log.ADDRESS))
