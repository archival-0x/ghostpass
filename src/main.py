#!/usr/bin/env python3

import names
import logging
import argparse

from getpass import getpass

import consts

'''

ghostpass help <command>
    - Prints help for a specific command

ghostpass init
    - Creates a new ghostpass session with master password
    - Pseudo-random ID created to identify session

ghostpass open <session>
    - Opens ghostpass session with master password
    - If only one session exists and session argument not provided,
    that is opened as default

ghostpass add <field>
    - Adds a new secret associated with <field> to current session

ghostpass remove <field>
    - Removes secret associated with <field> from current session

ghostpass view <field>
    - Shows unencrypted secret associated with <field> in current session

ghostpass list <session>
    - Shows all entries and associated IDs in current session
    - If only one session exists and session argument not provided,
    that is opened as default

ghostpass encrypt <corpus>
    - Creates encrypted ciphertext with specified corpus of current session
    - Works independent of whether user is in session or not

ghostpass decrypt <corpus> <ciphertext>
    - Decrypts specific ciphertext with corpus and master key
    - Works independent of whether user is in session or not

ghostpass destruct <session>
    - Destroys <session>
    - If only one session exists and session argument not provided,
    that is opened as default

'''

def man(argument):
    for k, v in consts.COMMANDS.items():
        if k == argument:
            print "\nHelp - " + k
            print v

def check_arg(argument):
    if not argument in consts.COMMANDS.keys():
        print "\nCommand '" + str(argument) + "' not found! Please specify one of these:\n"
        for arg in consts.COMMANDS:
            print arg
        print "\nFor more about each command individually, use 'ghostpass help <command>'"
        exit(1)

def main():
    # Initialize parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbosity', dest='verbosity', type=int, help='output based on verbosity level')
    parser.add_argument('command', nargs='+', help="Execute a specific command")

    args =  parser.parse_args()

    # Configure logging based on verbosity
    if args.verbosity == "1":
        log_level = logging.INFO
    elif args.verbosity == "2":
        log_level = logging.DEBUG

    command = args.command[0]

    # Check if specified command is valid
    check_arg(command)

    if len(args.command) == 2:
        value = args.command[1]

    # Print help for specified argument
    if command == "help":
        # Check if next value is a valid argument
        check_arg(value)
        # Print help for specific command
        man(value)

    # Initialize new session
    elif command == ""

if __name__ == '__main__':
    main()
