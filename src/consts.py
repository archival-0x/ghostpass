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

# dict represents all of our commands, plus their respective verbose help text
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
    - Changes should be STASHED to original session to save
""",
    'add': """
ghostpass add <field>
    - Adds a new secret associated with <field> to current session
""",
    'remove': """
ghostpass remove <field>
    - Removes secret associated with <field> from current session
""",
    'override': """
ghostpass remove <field>
    - Overrides secret associated with <field> from current session
""",
    'view': """
ghostpass view <field>
    - Shows unencrypted secret associated with <field> in current session
""",
    'stash': """
ghostpass stash
    - Commits changes made in opened session
    - Does not close session, but only writes changes to it
""",
    'list': """
ghostpass list
    - Shows all sessions created by user
""",
    'secrets': """
ghostpass secrets
    - Shows all fields and respective secrets in current session
""",
    'encrypt': """
ghostpass encrypt <corpus> <cleartext>
    - Creates encrypted ciphertext with specified corpus of current session
    - Works independent of whether user is in session or not
    - If no session is opened, cleartext field is mandatory for session-less encryption
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
