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
            sys.stdout.write("" + k + " ")
    print "\n\nEnter ghostpass help <command> for more information about a specific command\n"


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

    # Preemptive argument checking to see if necessary (one) field is provided
    # REQUIRED - add, remove, view, override, destruct
    # OPTIONAL - open
    # NO ARGS - init, list, secrets, close, help
    logging.debug("Checking if specific commands satisfy with args specification")
    if command in ["add", "remove", "view", "destruct", "override"] and len(args.command) != 2:
        man(command)
        raise ghostpass.GhostpassException("{} command requires at least one field argument".format(command))

    # Now check for arguments with multiple fields
    # MULTIPLE - encrypt, decrypt
    #   - note that for 'encrypt', one OR two arguments CAN be specified, and NO arguments will fail
    elif command == "encrypt" and not (len(args.command) >= 2 and len(args.command) <= 3):
        man(command)
        raise ghostpass.GhostpassException("{} command requires at least one field argument".format(command))

    #   - note that for 'decrypt', BOTH arguments are REQUIRED
    elif command == "decrypt" and not len(args.command) == 3:
        man(command)
        raise ghostpass.GhostpassException("{} command requires at two field arguments".format(command))

    # grab a list of all sessions within config path
    # TODO: robustness by checking validity of session file, to ensure no invalid/malicious JSON files are present
    sessions = [os.path.splitext(f)[0]
        for f in os.listdir(consts.DEFAULT_CONFIG_PATH)
        if os.path.isfile(os.path.join(consts.DEFAULT_CONFIG_PATH, f))
    ]

    # preemptive context file checking and opening - complete this for specific commands that require context file
    logging.debug("Checking if context file exists")
    if command in ["add", "remove", "override", "view", "stash", "secrets"]:
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
        print col.P + "Instantiating Ghostpass instance: " + col.C + gp.uuid + "\n" + col.W
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
            print col.O + "No session name specified, checking if only one (default) session exists..." + col.W
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
        print col.P + "Opening session: " + _gp.uuid + col.W
        contextpassword = getpass("> Enter MASTER PASSWORD (will not be echoed): ")
        if hashlib.sha256(contextpassword).hexdigest() != _gp.password:
            raise ghostpass.GhostpassException("incorrect master password for session: {}".format(_gp.uuid))

        # dump into pickle file
        logging.debug("Creating and writing context.pickle file")
        with open(consts.PICKLE_CONTEXT, 'wb') as context:
            pickle.dump(_gp, context)

        # TODO: peform decryption

        print col.G + "Session {} successfully opened!".format(_gp.uuid) + col.W
        return 0

    elif command == "close":
        # check if context.pickle exists, and deletes it
        logging.debug("Checking to see if context exists, and deleting")
        try:
            os.remove(consts.PICKLE_CONTEXT)
        except OSError: # uses exception handler in case file wasn't available in first place
            print col.O + "No session opened, so none closed" + col.W
            return 0

        print col.G + "Session successfully closed!" + col.W
        return 0

    elif command == "add":

        print col.P + "Adding field: " + args.command[1] + col.W + "\n"

        # retrieve secret for specific field
        username = raw_input("> Enter USERNAME for the field: ")
        secret = getpass("> Enter PASSWORD for field (will NOT be echoed): ")

        # securely append field and secret to session context
        if _gp.add_field(args.command[1], username, secret) == 0:
            with open(consts.PICKLE_CONTEXT, 'wb') as context:
                pickle.dump(_gp, context)
        else:
            raise ghostpass.GhostpassException("unable to add field: {}".format(args.command[1]))

        # ensure cleartext secret is NOT cached
        del secret

        return 0

    elif command == "remove":

        print col.P + "Removing field: " + args.command[1] + col.W

        # securely remove field and secret from session context
        if _gp.remove_field(args.command[1]) == 0:
            print col.G + "Success! Removed {}".format(args.command[1]) + col.W
            with open(consts.PICKLE_CONTEXT, 'wb') as context:
                pickle.dump(_gp, context)
        else:
            raise ghostpass.GhostpassException("unable to remove field: {}".format(args.command[1]))
        return 0

    elif command == "view":

        # calls view_field()
        logging.debug("Outputting unencrypted field")
        print "\n", _gp.view_field(args.command[1]), "\n"
        return 0

    elif command == "stash":

        # TODO: reencrypt all field passwords
        return 0

    elif command == "secrets":

        # list out all secrets for particular session
        logging.debug("Listing all secrets for this session")
        print "\n", _gp.view_all(), "\n"
        return 0

    elif command == "list":
        # recursively list all sessions
        logging.debug("Listing all available sessions")

        # if no session are available
        if len(sessions) == 0:
            print col.O + "No sessions available! Use `ghostpass init` to create a new one!" + col.W
            return 0

        print "------------------\nAvailable Sessions\n------------------\n"
        for s in sessions:
            print s
        print "\n-----------\n"
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
            print col.P + "Utilizing opened session for encryption: " + col.B + _gp.uuid + col.W
        else:
            # create a new temporary object for encryption
            _gp = ghostpass.Ghostpass()
            print col.P + "No session opened. Please supply master password for independent session-less encryption" + col.W
            masterpassword = getpass("> Enter MASTER PASSWORD (will not be echoed): ")

            # initializing state with password
            logging.debug("Initializing ghostpass object state")
            _gp.init_state(masterpassword)

            del masterpassword

        # load corpus file into object
        logging.debug("Loading corpus")
        _gp.load_corpus(args.command[1])

        # perform actual encryption
        logging.debug("Performing encryption")
        if len(args.command) == 3:
            # if optional second argument file (represents cleartext)
            _gp.encrypt_file(args.command[2])
        else:
            _gp.encrypt()

        return 0

    elif command == "decrypt":

        # perform file-checking
        logging.debug("Checking if specified files exist")
        if not os.path.isfile(args.command[1]) and os.path.isfile(args.command[2]):
            raise ghostpass.GhostpassException("file(s) specified do not exist")

        # since decrypt does not manipulate sessions, no context-checking is necessary
        logging.debug("Performing decryption")

        # create object for decrypt functionality
        _gp = ghostpass.Ghostpass()
        masterpassword = getpass("> Enter MASTER PASSWORD (will not be echoed): ")
        _gp.init_state(masterpassword)
        del masterpassword

        # decrypt the file, and export and output the resultant
        with open(decrypt(args.command[1], args.command[2]), 'w') as export:
            print export

        return 0

    elif command == "destruct":

        # check if session exists
        logging.debug("Checking to see if specified session exists")
        if not os.path.isfile(consts.DEFAULT_CONFIG_PATH + "/" + args.command[1]):
            raise ghostpass.GhostpassException("session does not exist.")

        # check if session is currently open as context
        logging.debug("Checking to see if specified session is opened")
        if os.path.isfile(consts.PICKLE_CONTEXT):
            context =  open(consts.PICKLE_CONTEXT, 'r')
            cgp = pickle.load(context)
            context.close()
            if cgp.uuid == args.command[1]:
                raise ghostpass.GhostpassException("session is currently open. Please close before destructing")

        # explicitly get user permission, and delete the session
        yn = raw_input("\n\t> Are you sure you want to delete this session? (y / n) ")
        if yn == "y" or yn == "yes":
            os.remove(consts.DEFAULT_CONFIG_PATH + "/" + args.command[1])
            print "\n" + col.G + "Succesfully deleted session " + args.command[1] + "!" + col.W

        return 0


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print col.O + "\n[*] Abrupt exit detected. Shutting down." + col.W
        exit(1)
