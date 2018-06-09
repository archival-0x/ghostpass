#!/usr/bin/env python2

import argparse
import sys
import os
import logging
import hashlib
import pickle
import jsonpickle

import consts
import ghostpass

from getpass import getpass
from consts import Color as col


def man(argument):
    '''
    helper manpages-style method for displaying information on positional
    arguments and any details
    '''

    # Print header if no arg is provided
    if argument is None or argument == "all":
        print "------------------\nAvailable Commands\n------------------\n"
    else:
        check_arg(argument)

    # Iterate over commands and check to see if any match argument, if provided
    for k, v in consts.COMMANDS.items():
        # print specific help menu for argument
        if k == argument:
            print "-----------"
            print "\nHelp - " + k
            print v
        # otherwise, print available args
        if argument is None or argument == "all":
            print k
    print "-----------\nEnter ghostpass help <command> for more information about a specific command\n"


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

    # Check to see if config path exists, and if not, create it
    logging.debug("Checking if config path exists")
    if not os.path.exists(consts.DEFAULT_CONFIG_PATH):
        # prevent race condition, as specified in
        # https://stackoverflow.com/questions/273192/how-can-i-create-a-directory-if-it-does-not-exist
        try:
            os.makedirs(consts.DEFAULT_CONFIG_PATH)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    # Set command as first argument provided
    command = args.command[0]

    # Check if specified command is valid
    logging.debug("Checking if provided argument is correct")
    if check_arg(command) != 0:
        raise ghostpass.GhostpassException("invalid command")

    # Preemptive argument checking to see if necessary field is provided
    # REQUIRED - add, remove, view
    # OPTIONAL - open, destruct
    # NO ARGS - init, list
    logging.debug("Checking if specific commands satisfy with second argument arguments")
    if command in ["add", "remove", "view"]:
        # Check if field argument is present
        if len(args.command) != 2:
            man(command)
            raise ghostpass.GhostpassException("{} command requires field argument".format(command))

    # Now check for arguments with multiple fields
    # MULTIPLE - encrypt, decrypt
    logging.debug("Checking if extra arguments were provided (max 2)")
    if not command in ["encrypt", "decrypt"] and len(args.command) > 2:
        raise ghostpass.GhostpassException("extraneous argument(s) provided")
    elif command in ["encrypt", "decrypt"] and len(args.command) > 3:
        raise ghostpass.GhostpassException("extraneous argument(s) provided")

    # grab a list of all sessions within config path
    # TODO: robustness by checking validity of session file, to ensure no invalid/malicious JSON files are present
    sessions = [os.path.splitext(f)[0]
        for f in os.listdir(consts.DEFAULT_CONFIG_PATH)
        if os.path.isfile(os.path.join(consts.DEFAULT_CONFIG_PATH, f))
    ]

    # preemptive context file checking and opening - complete this for specific commands that require context file
    logging.debug("Checking if context file exists")
    if command in ["add", "remove", "stash"]:
        # check if context file exists before adding
        if not os.path.isfile(consts.PICKLE_CONTEXT):
            raise ghostpass.GhostpassException("no session has been opened")

        # load object from pickle
        logging.debug("Loading object from pickle")
        context =  open(consts.PICKLE_CONTEXT, 'r')
        _gp = pickle.load(context)
        context.close()

    logging.debug("Performing actual argument checking")

    # Print help for specified argument
    if command == "help":
        # Print help for specific command (if passed)
        if len(args.command) == 2:
            man(args.command[1])
        elif len(args.command) == 1:
            man(None)
        return 0

    # Initialize new session
    elif command == "init":
        # Instantiate ghostpass object with new pseudorandom uuid, retrieve password and corpus path
        logging.debug("Instantiating ghostpass object")
        gp = ghostpass.Ghostpass()

        # grabbing user input for master password and corpus path
        print col.P + "[*] Instantiating Ghostpass instance: " + col.C + gp.uuid + col.P + " [*]\n" + col.W
        masterpassword = getpass("> Enter MASTER PASSWORD (will not be echoed): ")

        # initializing state with password
        logging.debug("Initializing ghostpass object state")
        gp.init_state(masterpassword)

        # destroy cleartext password so is not cached
        del masterpassword

        # export ghostpass object to encrypted JSON file
        logging.debug("Exporting ghostpass to JSON")
        gp.export()
        return 0

    elif command == "open":

        # checking to see if a session is already open
        logging.debug("Checking if context file exists")
        if os.path.isfile(consts.PICKLE_CONTEXT):
            raise ghostpass.GhostpassException("session already open. Close before opening another one.")

        # if only command provided, perform checking to see if only one session exists
        logging.debug("Checking to see if only one session exists")
        if len(args.command) == 1:

            # if multiple sessions exist, print man, and throw exception
            print col.O + "[*] No session name specified, checking if only one (default) session exists... [*]" + col.W
            if len(sessions) > 1:
                man("open")
                raise ghostpass.GhostpassException("no session argument specified, but multiple exist. Please specify session for opening.")

            # set context_session as first entry in configuration path
            context_session = consts.DEFAULT_CONFIG_PATH + "/" + sessions[0]
        else:
            # otherwise, set context_session as what user specified
            context_session = consts.DEFAULT_CONFIG_PATH + "/" + args.command[1]

        # read JSON from session file
        logging.debug("Reading from specific session")
        jsonstring = open(context_session).read()
        _gp = jsonpickle.decode(jsonstring)

        logging.debug(_gp) # __repr__ to validify open successful

        # password authentication
        logging.debug("Performing password authentication")
        print col.P + "[*] Opening session: " + _gp.uuid + col.W
        contextpassword = getpass("> Enter MASTER PASSWORD (will not be echoed): ")
        if hashlib.sha512(contextpassword).hexdigest() != _gp.password:
            raise ghostpass.GhostpassException("incorrect master password for session: {}".format(_gp.uuid))

        # dump into pickle file
        logging.debug("Creating and writing context.pickle file")
        with open(consts.PICKLE_CONTEXT, 'wb') as context:
            pickle.dump(_gp, context)

        print col.G + "[*] Session {} successfully opened! [*]".format(_gp.uuid) + col.W
        return 0

    elif command == "close":
        # check if context.pickle exists, and deletes it
        logging.debug("Checking to see if context exists, and deleting")
        try:
            os.remove(consts.PICKLE_CONTEXT)
        except OSError: # uses exception handler in case file wasn't available in first place
            print col.O + "[*] No session opened, so none closed [*]" + col.W
            return 0

        print col.G + "[*] Session successfully closed! [*]" + col.W
        return 0

    elif command == "add":
        print col.P + "[*] Adding field: " + args.command[1] + col.W + "\n"

        # retrieve secret for specific field
        secret = getpass("> Enter SECRET for field (will NOT be echoed): ")

        # securely append field and secret to session context
        _gp.add_field(args.command[1], secret)

        # ensure cleartext secret is NOT cached
        del secret

        return 0

    elif command == "remove":
        print col.P + "[*] Removing field: " + args.command[1] + col.W

        # securely remove field and secret from session context
        _gp.remove_field(args.command[1], secret)
        print col.G + "[*] Success! Removed {} [*]".format(args.command[1]) + col.W

        return 0

    elif command == "view":
        print _gp.view_field(args.command[1])
        return 0

    elif command == "stash":
        return 0

    elif command == "list":
        # recursively list all sessions
        logging.debug("Listing all available sessions")
        print "------------------\nAvailable Sessions\n------------------\n"
        for s in sessions:
            print s
        print "\n-----------\n"
        return 0

    elif command == "secrets":
        return 0

    elif command == "encrypt":
        # since sessions are optional, we can check to see if it exists
        logging.debug("Checking if context file exists. If not, temporary object will be created")
        if os.path.isfile(consts.PICKLE_CONTEXT):
            # load object from pickle
            logging.debug("Loading object from pickle")
            context =  open(consts.PICKLE_CONTEXT, 'r')
            _gp = pickle.load(context)
            context.close()
            print col.P + "[*] Utilizing opened session for encryption:" + col.B + _gp.uuid + col.P + " [*]" + col.W
        else:
            # create a new temporary object for encryption
            _gp = ghostpass.Ghostpass()
            print col.P + "[*] No session opened. Please supply master password for independent session-less encryption [*]" + col.W
            masterpassword = getpass("> Enter MASTER PASSWORD (will not be echoed): ")

            # initializing state with password
            logging.debug("Initializing ghostpass object state")
            _gp.init_state(masterpassword)

            del masterpassword

        # load corpus file into object
        _gp.load_corpus(args.command[1])

        # TODO: actual encryption
        return 0

    elif command == "decrypt":
        print args.command[1], args.command[2]

    elif command == "destruct":

        # if only command provided, perform checking to see if only one session exists
        logging.debug("Checking to see if only one session exists")
        if len(args.command) == 1:
            # if multiple sessions exist, print man, and throw exception
            if len(sessions) > 1:
                man("destruct")
                raise ghostpass.GhostpassException("no session argument specified, but multiple exist. Please specify session for destruction.")

        # check if session exists
        logging.debug("Checking to see if specified session exists")
        if not os.path.isfile(DEFAULT_CONFIG_PATH + args.command[1]):
            raise ghostpass.GhostpassException("session does not exist.")

        

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        # ensure that session info is backed up into JSON
        # ensure proper write to pickle file, if necessary
        print col.O + "\n[*] Abrupt exit detected. Shutting down safely." + col.W
        exit(1)
