#!/usr/bin/env python3
"""
<Program Name>
  ghostpass

<Author>
  Alan Cao <ex0dus@codemuch.tech>

<Started>
  May 2018

<Purpose>
  This is the entry file for Ghostpass console interactions. This file
  comprises of the main method that enables the user to initialize a
  session and perform all operations needed to interact with that session.
  Several helper methods are also provided, specifically for working together
  with argparse in order to provide a better command-line experience for the
  user.

"""
import os
import sys
import logging
import argparse
import hashlib
import pickle
import jsonpickle
import getpass

from . import ghostpass
from . import consts
from .consts import Color as col


def man(argument):
    """
    <Purpose>
      Helper manpages-style method for displaying information on positional
      arguments and any details. It provides a much more verbose output
      for interfacing with the command-line application

    <Returns>
      None

    """

    # Print header if no arg is provided
    if argument is None or argument == "all":
        print("------------------\nAvailable Commands\n------------------\n")
    else:
        check_arg(argument)

    # Iterate over commands and check to see if any match argument, if provided
    for k, v in consts.COMMANDS.items():
        if k == argument:
            print("-----------")
            print("\nHelp - " + k)
            print(v)
        if argument is None or argument == "all":
            sys.stdout.write("" + k + " ")
    print("\n\nEnter ghostpass help <command> for more information about a specific command\n")




def check_arg(argument):
    """
    <Purpose>
      Argument-checking method that ensures that the specified command could be found

    <Returns>
      0 for success
      1 for failure

    """
    if not argument in consts.COMMANDS.keys():
        print("Command '" + str(argument) + "' not found! Please specify one of these:\n")
        sys.stdout.write("\t")
        for arg in consts.COMMANDS:
            sys.stdout.write("" + arg + " ")
        print("\n\nFor more about each command individually, use 'ghostpass help <command>'")
        return 1
    return 0





def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbosity', dest='verbosity', type=int, help='output based on verbosity level')
    parser.add_argument('command', nargs='+', help="Execute a specific command")

    args = parser.parse_args()

    # configure logging based on verbosity
    if args.verbosity == 2:
        log_level = logging.DEBUG

    # use try/except to prevent race condition in creating config path
    logging.debug("Checking if config path exists")
    if not os.path.exists(consts.DEFAULT_CONFIG_PATH):
        try:
            os.makedirs(consts.DEFAULT_CONFIG_PATH)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    # check if specified command is valid
    logging.debug("Checking if provided argument is correct")
    command = args.command[0]
    if check_arg(command) != 0:
        raise ghostpass.GhostpassException("invalid command")

    # preemptive argument checking
    logging.debug("Checking if specific commands satisfy with args specification")

    # No fields - ./ghostpass COMMAND
    if command in consts.NO_FIELD and len(args.command) > 1:
        man(command)
        raise ghostpass.GhostpassException("Extraneous arguments supplied for {} command".format(command))

    # Optional fields - ./ghostpass COMMAND or ./ghostpass COMMAND <field>
    elif command in consts.OPTIONAL_FIELD:
        if len(args.command) != 1 and len(args.command) != 2:
            man(command)
            raise ghostpass.GhostpassException("{} command requires at most one field argument".format(command))

    # Required field - ./ghostpass COMMAND <field>
    elif command in consts.REQUIRED_FIELD and len(args.command) != 2:
        man(command)
        raise ghostpass.GhostpassException("{} command requires one field argument".format(command))

    # Two required fields - ./ghostpass COMMAND <field1> <field2>
    elif command in consts.REQUIRED_TWO_FIELD and len(args.command) != 3:
        man(command)
        raise ghostpass.GhostpassException("{} command requires two field arguments".format(command))

    # grab a list of all sessions within config path
    # TODO: robustness by checking validity of session file, to ensure no invalid JSON files are present
    sessions = [os.path.splitext(f)[0]
        for f in os.listdir(consts.DEFAULT_CONFIG_PATH)
        if os.path.isfile(os.path.join(consts.DEFAULT_CONFIG_PATH, f))
    ]

    # preemptive context file checking and opening - complete this for specific commands that require context file
    logging.debug("Checking if context file exists")
    if command in consts.REQUIRED_CONTEXT:

        # check if context file exists before adding
        if not os.path.isfile(consts.PICKLE_CONTEXT):
            raise ghostpass.GhostpassException("no session has been opened")

        # load object from pickle
        logging.debug("Loading object from pickle")
        with open(consts.PICKLE_CONTEXT, 'r') as context:
            _gp = pickle.load(context)


    logging.debug("Performing actual argument checking")
    if command == "help":

        # print help for specific command (if passed)
        if len(args.command) == 2:
            man(args.command[1])
        else:
            man(None)

    elif command == "init":
        logging.debug("Instantiating ghostpass object")

        # instantiate ghostpass object with new pseudorandom uuid, retrieve password and corpus path
        gp = ghostpass.Ghostpass()

        # grabbing user input for master password and corpus path
        print(col.P + "Instantiating Ghostpass instance: " + col.C + gp.uuid + "\n" + col.W)
        masterpassword = getpass.getpass("> Enter MASTER PASSWORD (will not be echoed): ")
        corpus_path = input("> Enter DOCUMENT KEY path: ")

        # initializing state with password
        logging.debug("Initializing ghostpass object state")
        gp.init_state(masterpassword, corpus_path)

        # destroy cleartext password so is not cached
        del masterpassword

        # export ghostpass object to encrypted JSON file
        logging.debug("Exporting ghostpass to JSON")
        gp.export()

        print(col.G + "\nCreated new session! Remember your password, and use `ghostpass open <SESSION>` to open it!" + col.W)


    elif command == "whoami":
        print(col.G + "\n" + _gp.uuid + "is currently open." + col.W)

    elif command == "open":

        # checking to see if a session is already open
        logging.debug("Checking if context file exists")
        if os.path.isfile(consts.PICKLE_CONTEXT):
            raise ghostpass.GhostpassException("session already open. Close before opening another one.")

        # if only command provided, perform checking to see if only one session exists
        logging.debug("Checking to see if only one session exists")
        if len(args.command) == 1:

            # if multiple sessions exist, print man, and throw exception
            print(col.O + "No session name specified, checking if only one (default) session exists..." + col.W)
            if len(sessions) > 1:
                man("open")
                raise ghostpass.GhostpassException("no session argument specified, but multiple exist. Please specify session for opening.")
            elif len(sessions) == 0:
                raise ghostpass.GhostpassException("no sessions exist. Use `ghostpass init` to create a new one.")

            # set context_session as first entry in configuration path
            context_session = consts.DEFAULT_CONFIG_PATH + "/" + sessions[0]
        else:
            # otherwise, set context_session as what user specified
            context_session = consts.DEFAULT_CONFIG_PATH + "/" + args.command[1]

        # read JSON from session file
        logging.debug("Reading from specific session")
        try:
            jsonstring = open(context_session).read()
        except IOError:
            raise ghostpass.GhostpassException("{} is not a valid session.".format(context_session))
        _gp = jsonpickle.decode(jsonstring)
        logging.debug(_gp)

        # password authentication
        print(col.P + "Opening session: " + _gp.uuid + col.W)
        contextpassword = getpass.getpass("> Enter MASTER PASSWORD (will not be echoed): ")
        if hashlib.sha512(contextpassword).digest() != _gp.password:
            raise ghostpass.GhostpassException("incorrect master password for session: {}".format(_gp.uuid))

        # dump into pickle file
        logging.debug("Creating and writing context.pickle file")
        with open(consts.PICKLE_CONTEXT, 'wb') as context:

            # decrypt and write
            if len(_gp.data) != 0:
                logging.debug("Decrypting fields in data")
                _gp.decrypt_fields()
            pickle.dump(_gp, context)

        print(col.G + "Session {} successfully opened!".format(_gp.uuid) + col.W)


    elif command == "close":
        logging.debug("Checking to see if context exists, and deleting")
        try:
            os.remove(consts.PICKLE_CONTEXT)
        except OSError: # uses exception handler in case file wasn't available in first place
            print(col.O + "No session opened, so none closed" + col.W)
            return
        print(col.G + "Session closed!" + col.W)


    elif command == "add":
        print(col.P + "Adding field: " + args.command[1] + col.W + "\n")

        # retrieve secret for specific field
        username = input("> Enter USERNAME for the field: ")
        secret = getpass.getpass("> Enter PASSWORD for field (will NOT be echoed): ")

        # securely append field and secret to session context
        if _gp.add_field(args.command[1], username, secret) == 0:
            with open(consts.PICKLE_CONTEXT, 'wb') as context:
                pickle.dump(_gp, context)
        else:
            raise ghostpass.GhostpassException("unable to add field: {}".format(args.command[1]))

        # ensure cleartext secret is NOT cached
        del secret


    elif command == "remove":
        logging.debug("Removing field " + args.command[1])

        # securely remove field and secret from session context
        if _gp.remove_field(args.command[1]) == 0:
            print(col.G + "Success! Removed {}".format(args.command[1]) + col.W)
            with open(consts.PICKLE_CONTEXT, 'wb') as context:
                pickle.dump(_gp, context)
        else:
            raise ghostpass.GhostpassException("unable to remove field: {}".format(args.command[1]))


    elif command == "view":
        logging.debug("Outputting unencrypted field as a pretty-table")
        print("\n", _gp.view_field(args.command[1]), "\n")


    elif command == "stash":
        logging.debug("Re-encrypting all secrets.")
        _gp.encrypt_fields()

        logging.debug("Writing to session.")
        with open(consts.DEFAULT_CONFIG_PATH + "/" + _gp.uuid, 'w') as context:
            json_obj = jsonpickle.encode(_gp)
            context.write(json_obj)


    elif command == "secrets":
        logging.debug("Listing all secrets for this session")
        print("\n", _gp.view_all(), "\n")


    elif command == "list":
        logging.debug("Listing all available sessions")

        if len(sessions) == 0:
            print(col.O + "No sessions available! Use `ghostpass init` to create a new one!" + col.W)
            return 0

        print("------------------\nAvailable Sessions\n------------------\n")
        for s in sessions:
            print(s)
        print("\n-----------\n")


    elif command == "encrypt":

        # ensure that our changes have been committed back to the original session file
        logging.debug("Checking if changes were stashed")
        if _gp.encrypted == False:
            print(col.O + "Changes have NOT been stashed. Stashing changes automatically." + col.W)
            _gp.stash_changes()

        # export encrypted file of our secrets
        encrypt_out = _gp.encode_files()
        with open(consts.NOW_TIME + "-encrypted.txt", "wb") as output:
            output.write(encrypt_out)


    elif command == "decrypt":

        logging.debug("Checking if specified files exist")
        if not os.path.isfile(args.command[1]) and os.path.isfile(args.command[2]):
            raise ghostpass.GhostpassException("file(s) specified do not exist")

        # since decrypt does not manipulate sessions, no context-checking is necessary
        # create an isolated temporary object for decrypt functionality
        logging.debug("Performing decryption")
        decrypt_gp = ghostpass.Ghostpass()
        masterpassword = getpass.getpass("> Enter MASTER PASSWORD (will not be echoed): ")
        decrypt_gp.init_state(masterpassword)
        del masterpassword

        # load corpus file into object
        logging.debug("Loading corpus")
        with open(args.command[1], 'r') as cf:
            corpus = cf.readlines()
        decrypt_gp.load_corpus(corpus)

        # decrypt the file, and export and output
        decrypt_out = decrypt_gp.decode_file(args.command[1], args.command[2])
        with open(consts.NOW_TIME + "-decrypted.txt", "wb") as output:
            output.write(decrypt_out)


    elif command == "destruct":

        # check if session exists
        logging.debug("Checking to see if specified session exists")
        if not os.path.isfile(consts.DEFAULT_CONFIG_PATH + "/" + args.command[1]):
            raise ghostpass.GhostpassException("session does not exist.")

        # check if session is currently open as context
        logging.debug("Checking to see if specified session is opened")
        if os.path.isfile(consts.PICKLE_CONTEXT):
            with open(consts.PICKLE_CONTEXT, 'r') as context:
                cgp = pickle.load(context)
                if cgp.uuid == args.command[1]:
                    raise ghostpass.GhostpassException("session is currently open. Please close before destructing")

        # explicitly get user permission, and delete the session
        yn = input("\n> Are you sure you want to delete this session? (y / n) ")
        if yn == "y" or yn == "yes":
            os.remove(consts.DEFAULT_CONFIG_PATH + "/" + args.command[1])
            print("\n" + col.G + "Succesfully deleted session " + args.command[1] + "!" + col.W)

    return 0



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(col.O + "\n[*] Abrupt exit detected. Shutting down." + col.W)
        exit(1)
