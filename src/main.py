#!/usr/bin/env python3

import names
import logging
import argparse

from getpass import getpass

import consts
import ghostpass



'''
    man(argument)
        - helper manpages-style method for displaying information on positional
        arguments and any details
'''
def man(argument):
    # Print header if no arg is provided
    if argument is None or argument == "all":
        print "\nAvailable Commands (enter ghostpass help <command>) for more information\n"
    else:
        check_arg(argument)

    # Iterate over commands and check to see if any match argument, if provided
    for k, v in consts.COMMANDS.items():
        # print specific help menu for argument
        if k == argument:
            print "\nHelp - " + k
            print v
        # otherwise, print available args
        if argument is None or argument == "all":
            print k

def check_arg(argument):
    if not argument in consts.COMMANDS.keys():
        print "\nCommand '" + str(argument) + "' not found! Please specify one of these:\n"
        for arg in consts.COMMANDS:
            print arg
        print "\nFor more about each command individually, use 'ghostpass help <command>'"
        return 1
    return 0

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

    # Set command as first argument provided
    command = args.command[0]

    # Check if specified command is valid
    if check_arg(command) != 0:
        raise ghostpass.GhostpassException("invalid command")

    # Check if len of arguments is 2
    if len(args.command) > 2:
        raise ghostpass.GhostpassException("extraneous argument provided")

    # Print help for specified argument
    if command == "help":
        # Check if next value is a valid argument
        if check_arg(command) != 0:
            raise ghostpass.GhostpassException("invalid command")

        # Print help for specific command (if passed)
        if len(args.command) == 2:
            man(args.command[1])
        elif len(args.command) < 2:
            man(None)

    # Initialize new session
    elif command == "init":
        print command
    elif command == "open":
        print command

if __name__ == '__main__':
    main()
