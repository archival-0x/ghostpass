#!/usr/bin/env python2

import argparse
import sys
import readline
import glob
import logging

import consts
import ghostpass

from getpass import getpass
from consts import Color as col


def pathcomplete(text, state):
    """
    This is the tab completer for systems paths.
    Only tested on *nix systems
    """
    line = readline.get_line_buffer().split()

    # replace ~ with the user's home dir. See https://docs.python.org/2/library/os.path.html
    if '~' in text:
        text = os.path.expanduser('~')

    # autocomplete directories with having a trailing slash
    if os.path.isdir(text):
        text += '/'

    return [x for x in glob.glob(text + '*')][state]

def man(argument):
    '''
    helper manpages-style method for displaying information on positional
    arguments and any details
    '''

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
    '''
    ensures that passed argument can be supplied
    '''
    if not argument in consts.COMMANDS.keys():
        print "Command '" + str(argument) + "' not found! Please specify one of these:\n"
        sys.stdout.write("\t")
        for arg in consts.COMMANDS:
            sys.stdout.write("" + arg + " ")
        print "\n\nFor more about each command individually, use 'ghostpass help <command>'"
        return 1
    return 0


def main():
    # Initialize parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbosity', dest='verbosity', type=int, help='output based on verbosity level')
    parser.add_argument('command', nargs='+', help="Execute a specific command")

    args =  parser.parse_args()

    # Configure logging based on verbosity
    if args.verbosity == 2:
        log_level = logging.DEBUG

    # Set command as first argument provided
    command = args.command[0]

    # Check if specified command is valid
    logging.debug("Checking if provided argument is correct")
    if check_arg(command) != 0:
        raise ghostpass.GhostpassException("invalid command")

    # Check if len of arguments not over 2
    logging.debug("Checking if extra arguments were provided (max 2)")
    if command != "decrypt" and len(args.command) > 2:
        raise ghostpass.GhostpassException("extraneous argument(s) provided")
    elif command == "decrypt" and len(args.command) > 3:
        raise ghostpass.GhostpassException("extraneous argument(s) provided")

    # Preemptive argument checking to see if necessary field is provided
    # REQUIRED - add, remove, view, encrypt
    # OPTIONAL - open, list, destruct
    logging.debug("Checking if specific commands satisfy with second argument arguments")
    if command in ["add", "remove", "view", "encrypt"]:
        # Check if field argument is present
        if len(args.command) != 2:
            man(command)
            raise ghostpass.GhostpassException("{} command requires field argument".format(command))

    logging.debug("Performing actual argument checking")

    # Print help for specified argument
    if command == "help":

        # Print help for specific command (if passed)
        if len(args.command) == 2:
            man(args.command[1])
        elif len(args.command) == 1:
            man(None)

    # Initialize new session
    elif command == "init":

        # Instantiate ghostpass object with new pseudorandom uuid, retrieve password and corpus path
        logging.debug("Instantiating ghostpass object")
        gp = ghostpass.Ghostpass()

        # grabbing user input for master password and corpus path
        print "[*] Instantiating Ghostpass instance: ", col.C, gp.uuid,  col.W, "\n"
        masterpassword = getpass("> Enter MASTER PASSWORD (will not be echoed): ")

        logging.debug("Setting Unix path autocomplete")
        readline.set_completer_delims('\t')
        readline.parse_and_bind("tab: complete")
        readline.set_completer(pathcomplete)
        corpus_path = raw_input("> Enter CORPUS FILE PATH: ")

        # initializing state with password and corpus
        logging.debug("Initializing ghostpass object state")
        gp.init_state(masterpassword, corpus_path)

        # destroy cleartext password so is not cached
        del masterpassword

        # export ghostpass object to encrypted JSON file
        logging.debug("Exporting ghostpass to JSON")
        gp.export()

    elif command == "open":
        if len(arg.commands) == 1:
            # TODO: perform checking to see if only one session exists
            print ""

    elif command == "add":
        print args.command[1]

    elif command == "remove":
        print args.command[1]

    elif command == "list":
        print args.command[1]

    elif command == "encrypt":
        print args.command[1]

    elif command == "decrypt":
        print args.command[1], args.command[2]

    elif command == "destruct":
        print args.command[1]


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        # ensure that session info is backed up into JSON
        print "[*] Abrupt exit detected. Shutting down safely."
        exit(1)
