"""
<Program Name>
    consts.py

<Purpose>
    Application-level constant variables made available for all
    files
"""

import os
import time 

NAME = "ghostpass"
VERSION = "0.0.1"

NOW_DATE = time.strftime("%Y-%m-%d-%H:%M:%S", time.gmtime())

# filepath configuration constants
DEFAULT_CONFIG_PATH = os.path.dirname(os.path.expanduser("~") + "/.config/ghostpass/")
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PICKLE_CONTEXT = ROOT_DIR + "/" + 'context.pickle'

# markov cipher constants
MARKOV_START = "<MARKOV_START>"
MIN_LINE_LEN = 4

# lookup table for bit expansion factor of 3
EXPANSION_TABLE = [
    00000000, 0x000007, 0x000038, 0x00003f, 0x0001c0, 0x0001c7, 0x0001f8, 0x0001ff,
    0x000e00, 0x000e07, 0x000e38, 0x000e3f, 0x000fc0, 0x000fc7, 0x000ff8, 0x000fff,
    0x007000, 0x007007, 0x007038, 0x00703f, 0x0071c0, 0x0071c7, 0x0071f8, 0x0071ff,
    0x007e00, 0x007e07, 0x007e38, 0x007e3f, 0x007fc0, 0x007fc7, 0x007ff8, 0x007fff,
    0x038000, 0x038007, 0x038038, 0x03803f, 0x0381c0, 0x0381c7, 0x0381f8, 0x0381ff,
    0x038e00, 0x038e07, 0x038e38, 0x038e3f, 0x038fc0, 0x038fc7, 0x038ff8, 0x038fff,
    0x03f000, 0x03f007, 0x03f038, 0x03f03f, 0x03f1c0, 0x03f1c7, 0x03f1f8, 0x03f1ff,
    0x03fe00, 0x03fe07, 0x03fe38, 0x03fe3f, 0x03ffc0, 0x03ffc7, 0x03fff8, 0x03ffff,
    0x1c0000, 0x1c0007, 0x1c0038, 0x1c003f, 0x1c01c0, 0x1c01c7, 0x1c01f8, 0x1c01ff,
    0x1c0e00, 0x1c0e07, 0x1c0e38, 0x1c0e3f, 0x1c0fc0, 0x1c0fc7, 0x1c0ff8, 0x1c0fff,
    0x1c7000, 0x1c7007, 0x1c7038, 0x1c703f, 0x1c71c0, 0x1c71c7, 0x1c71f8, 0x1c71ff,
    0x1c7e00, 0x1c7e07, 0x1c7e38, 0x1c7e3f, 0x1c7fc0, 0x1c7fc7, 0x1c7ff8, 0x1c7fff,
    0x1f8000, 0x1f8007, 0x1f8038, 0x1f803f, 0x1f81c0, 0x1f81c7, 0x1f81f8, 0x1f81ff,
    0x1f8e00, 0x1f8e07, 0x1f8e38, 0x1f8e3f, 0x1f8fc0, 0x1f8fc7, 0x1f8ff8, 0x1f8fff,
    0x1ff000, 0x1ff007, 0x1ff038, 0x1ff03f, 0x1ff1c0, 0x1ff1c7, 0x1ff1f8, 0x1ff1ff,
    0x1ffe00, 0x1ffe07, 0x1ffe38, 0x1ffe3f, 0x1fffc0, 0x1fffc7, 0x1ffff8, 0x1fffff,
    0xe00000, 0xe00007, 0xe00038, 0xe0003f, 0xe001c0, 0xe001c7, 0xe001f8, 0xe001ff,
    0xe00e00, 0xe00e07, 0xe00e38, 0xe00e3f, 0xe00fc0, 0xe00fc7, 0xe00ff8, 0xe00fff,
    0xe07000, 0xe07007, 0xe07038, 0xe0703f, 0xe071c0, 0xe071c7, 0xe071f8, 0xe071ff,
    0xe07e00, 0xe07e07, 0xe07e38, 0xe07e3f, 0xe07fc0, 0xe07fc7, 0xe07ff8, 0xe07fff,
    0xe38000, 0xe38007, 0xe38038, 0xe3803f, 0xe381c0, 0xe381c7, 0xe381f8, 0xe381ff,
    0xe38e00, 0xe38e07, 0xe38e38, 0xe38e3f, 0xe38fc0, 0xe38fc7, 0xe38ff8, 0xe38fff,
    0xe3f000, 0xe3f007, 0xe3f038, 0xe3f03f, 0xe3f1c0, 0xe3f1c7, 0xe3f1f8, 0xe3f1ff,
    0xe3fe00, 0xe3fe07, 0xe3fe38, 0xe3fe3f, 0xe3ffc0, 0xe3ffc7, 0xe3fff8, 0xe3ffff,
    0xfc0000, 0xfc0007, 0xfc0038, 0xfc003f, 0xfc01c0, 0xfc01c7, 0xfc01f8, 0xfc01ff,
    0xfc0e00, 0xfc0e07, 0xfc0e38, 0xfc0e3f, 0xfc0fc0, 0xfc0fc7, 0xfc0ff8, 0xfc0fff,
    0xfc7000, 0xfc7007, 0xfc7038, 0xfc703f, 0xfc71c0, 0xfc71c7, 0xfc71f8, 0xfc71ff,
    0xfc7e00, 0xfc7e07, 0xfc7e38, 0xfc7e3f, 0xfc7fc0, 0xfc7fc7, 0xfc7ff8, 0xfc7fff,
    0xff8000, 0xff8007, 0xff8038, 0xff803f, 0xff81c0, 0xff81c7, 0xff81f8, 0xff81ff,
    0xff8e00, 0xff8e07, 0xff8e38, 0xff8e3f, 0xff8fc0, 0xff8fc7, 0xff8ff8, 0xff8fff,
    0xfff000, 0xfff007, 0xfff038, 0xfff03f, 0xfff1c0, 0xfff1c7, 0xfff1f8, 0xfff1ff,
    0xfffe00, 0xfffe07, 0xfffe38, 0xfffe3f, 0xffffc0, 0xffffc7, 0xfffff8, 0xffffff
]

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


# commands that take no input fields
NO_FIELD = [
    "init",
    "whoami",
    "list",
    "secrets",
    "close",
    "encrypt",
    "help"
]

# commands that require one input field
REQUIRED_FIELD = [
    "add",
    "remove",
    "override",
    "view",
    "destruct",
    "override"
]

# commands that have optional input field
OPTIONAL_FIELD = [
    "open"
]

# commands that require two input fields
REQUIRED_TWO_FIELD = [
    "decrypt"
]

# commands that require a session to be opened
REQUIRED_CONTEXT = [
    "whoami",
    "add",
    "remove",
    "override",
    "view",
    "stash",
    "secrets",
    "encrypt"
]

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
    'whoami': """
ghostpass whoami
    - Outputs current session name, if opened.
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
