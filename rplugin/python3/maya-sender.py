import sys
import os

import pynvim


import sender

PATH = os.path.dirname(os.path.abspath(__file__))
if PATH not in sys.path:
    sys.path.append(PATH)


@pynvim.plugin
class MayaSender:
    def __init__(self, nvim: pynvim.Nvim):
        self.nvim = nvim

        self.options = {
            "address": "127.0.0.1",
            "port": 5115,
            "logger_port": 5116,
        }

        self.setup()

    def setup(self):
        for option, default in self.options.items():
            try:
                variable = f"MayaSender_{option}"
                self.options[option] = self.nvim.eval(f"g:{variable}")
            except self.nvim.error:
                self.options[option] = default

        self.ADDRESS = (self.options["address"], self.options["port"])

    @pynvim.command("MayaSendSelection")
    def send_selection(self):
        self._reload_project_module()
        sender.send_selection(self.nvim, self.ADDRESS)

    @pynvim.command("MayaSendBuffer")
    def send_buffer(self):
        self._reload_project_module()
        sender.send_buffer(self.nvim, self.ADDRESS)

    def _reload_project_module(self):
        reloader_path = PATH + "/reloader.py"
        cwd = self.nvim.command_output("pwd")

        sender.send_command(f'exec(open("{reloader_path}").read())', self.ADDRESS)
        sender.send_command(f"import reloader; reloader.reload('{cwd}')", self.ADDRESS)
