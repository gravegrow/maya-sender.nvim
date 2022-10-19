import os
import sys

from pynvim import Nvim, command, plugin

PATH = os.path.dirname(os.path.abspath(__file__))
if PATH not in sys.path:
    sys.path.append(PATH)

    import log
    import sender


@plugin
class MayaScriptEditor:
    def __init__(self, nvim: Nvim):
        self.nvim = nvim
        self.log_window = log.Window(nvim)

    @command('MayaSendSelection', sync=True)
    def send_selection(self):
        sender.send_selection(self.nvim)

    @command('MayaSendBuffer', sync=True)
    def send_buffer(self):
        sender.send_buffer(self.nvim)

    @command('MayaOpenLog', sync=True)
    def toggle_log_widnow(self):
        self.log_window.toggle()
        if self.log_window.is_opened:
            sender.ensure_stream()

    @command('MayaConnect', sync=True)
    def start_stream(self):
        sender.ensure_stream()

    @command('MayaDisconnect', sync=True)
    def stop_stream(self):
        sender.stop_stream()