import os

PATH = os.path.dirname(os.path.abspath(__file__))
SERVER = "127.0.0.1"
COMMAND_PORT = 5115
COMMAND_ADDRESS = (SERVER, COMMAND_PORT)

MODULE_FILE = os.path.abspath(__file__)
MODULE_PATH = os.path.dirname(MODULE_FILE)
MODULE_NAME = os.path.basename(MODULE_PATH)

LOGGER_PORT = 5116
LOGGER_ADDRESS = (SERVER, LOGGER_PORT)
