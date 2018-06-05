'''
    consts.py
        Application-level constant variables
'''
import os

NAME = "ghostpass"
VERSION = "0.0.1"

DEFAULT_CONFIG_PATH = os.path.dirname(os.path.expanduser("~") + "/.config/ghostpass/")
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PICKLE_CONTEXT = ROOT_DIR + "/" + 'context.pickle'

LOGO = """
  ________.__                    __
 /  _____/|  |__   ____  _______/  |____________    ______ ______
/   \  ___|  |  \ /  _ \/  ___/\   __\____ \__  \  /  ___//  ___/
\    \_\  \   Y  (  <_> )___ \  |  | |  |_> > __ \_\___ \ \___ \
 \______  /___|  /\____/____  > |__| |   __(____  /____  >____  >
        \/     \/           \/       |__|       \/     \/     \/
"""

# Class for color variables, inheritable throughout entirety of code
class Color:
    W = '\033[0m'  # white (normal)
    R = '\033[31m'  # red
    G = '\033[32m'  # green
    O = '\033[33m'  # orange
    B = '\033[34m'  # blue
    P = '\033[35m'  # purple
    C = '\033[36m'  # cyan
    GR = '\033[37m' # gray

# dict represents all of our commands, plus there respective verbose help text
COMMANDS = {
    'help': """
ghostpass help <command>
    - Prints help for a specific command
""",
    'init': """
ghostpass init
    - Creates a new ghostpass session with master password
    - Pseudo-random ID created to identify session
""",
    'open': """
ghostpass open <session>
    - Opens ghostpass session with master password
    - If only one session exists and session argument not provided,
    that is opened as default
""",
    'close': """
ghostpass close
    - Closes ghostpass session, if any is opened
""",
    'add': """
ghostpass add <field>
    - Adds a new secret associated with <field> to current session
""",
    'remove': """
ghostpass remove <field>
    - Removes secret associated with <field> from current session
""",
    'view': """
ghostpass view <field>
    - Shows unencrypted secret associated with <field> in current session
""",
    'list': """
ghostpass list
    - Shows all sessions created by user
""",
    'secrets': """
ghostpass secrets
    - Shows all entries and associated IDs in current session
""",
    'encrypt': """
ghostpass encrypt <corpus>
    - Creates encrypted ciphertext with specified corpus of current session
    - Works independent of whether user is in session or not
""",
    'decrypt': """
ghostpass decrypt <corpus> <ciphertext>
    - Decrypts specific ciphertext with corpus and master key
    - Works independent of whether user is in session or not
""",
    'destruct': """
ghostpass destruct <session>
    - Destroys <session>
    - If only one session exists and session argument not provided,
    that is opened as default
"""
}
