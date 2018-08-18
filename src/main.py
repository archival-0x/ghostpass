#!/usr/bin/env python2
"""
<Program Name>
  main.py

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
    """
    <Purpose>
      Argument-checking method that ensures that the specified command could be found

    <Returns>
      0 for success
      1 for failure

    """
    if not argument in consts.COMMANDS.keys():
        print "Command '" + str(argument) + "' not found! Please specify one of these:\n"
        sys.stdout.write("\t")
        for arg in consts.COMMANDS:
            sys.stdout.write("" + arg + " ")
        print "\n\nFor more about each command individually, use 'ghostpass help <command>'"
        return 1
    return 0





def main():
    """
    <Purpose>
      This is the main entry point to the Ghostpass command line
      application. It initializes an argument parser, performs
      preemptive checking, and then calls upon necessary modules
      in order to work with the protocol
    
    <Returns>
      0 for success
      GhostpassException for errors
    
    """

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

    # Preemptive argument checking
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
    # TODO: robustness by checking validity of session file, to ensure no invalid/malicious JSON files are present
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
        corpus_path = raw_input("> Enter INITIAL DOCUMENT KEY path: ")

        # initializing state with password
        logging.debug("Initializing ghostpass object state")
        gp.init_state(masterpassword, corpus_path)

        # destroy cleartext password so is not cached
        del masterpassword

        # export ghostpass object to encrypted JSON file
        logging.debug("Exporting ghostpass to JSON")
        gp.export()

        print col.G + "\nCreated new session! Remember your password, and use `ghostpass open <SESSION>` to open it!" + col.W
        return 0
    
    # Check what session we are currently in
    elif command == "whoami":
        print col.G + "\n" + _gp.uuid + "is currently open." + col.W        
        return 0

    # Open an initialized session
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

        logging.debug(_gp) # __repr__ to validify open successful

        # password authentication
        logging.debug("Performing password authentication")
        print col.P + "Opening session: " + _gp.uuid + col.W
        contextpassword = getpass("> Enter MASTER PASSWORD (will not be echoed): ")
        
        # TODO: better password authentication - compare final doc keys generated from user-input
        if hashlib.sha512(contextpassword).digest() != _gp.password:
            raise ghostpass.GhostpassException("incorrect master password for session: {}".format(_gp.uuid))

        # dump into pickle file
        logging.debug("Creating and writing context.pickle file")
        with open(consts.PICKLE_CONTEXT, 'wb') as context:
            # decrypt fields if any fields have been written
            if len(_gp.data) != 0:
                logging.debug("Decrypting fields in data")
                _gp.decrypt_fields()

            # write object to context file
            pickle.dump(_gp, context)

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
        logging.debug("Outputting unencrypted field as a pretty-table")
        print "\n", _gp.view_field(args.command[1]), "\n"
        return 0

    elif command == "stash":

        # calling encrypt_fields() to re-encrypt all secrets
        logging.debug("Re-encrypting all secrets.")
        _gp.encrypt_fields()

        # writing encrypted structure to original session
        logging.debug("Writing to session.")
        with open(consts.DEFAULT_CONFIG_PATH + "/" + _gp.uuid, 'w') as context:
            json_obj = jsonpickle.encode(_gp)
            context.write(json_obj)

        # user calls 'close' to remove context.pickle
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

        # perform actual encryption
        logging.debug("Performing encryption")
        if len(args.command) == 3:
            # if optional second argument file (represents cleartext)
            _gp.encrypt_file(args.command[2])

            # export encrypted file of cleartext

        else:
            # check if changes have been stashed first
            if _gp.encrypted == False:
                print col.O + "Changes have NOT been stashed. Stashing changes automatically." + col.W
                _gp.stash_changes()

            # export encrypted file of our secrets


        return 0

    elif command == "decrypt":

        # perform file-checking
        logging.debug("Checking if specified files exist")
        if not os.path.isfile(args.command[1]) and os.path.isfile(args.command[2]):
            raise ghostpass.GhostpassException("file(s) specified do not exist")

        # since decrypt does not manipulate sessions, no context-checking is necessary
        logging.debug("Performing decryption")

        # create temporary object for decrypt functionality
        _gp = ghostpass.Ghostpass()
        masterpassword = getpass("> Enter MASTER PASSWORD (will not be echoed): ")
        _gp.init_state(masterpassword)
        del masterpassword

        # load corpus file into object
        logging.debug("Loading corpus")
        with open(args.command[1], 'r') as cf:
            corpus = cf.readlines()
        _gp.load_corpus(corpus)

        # decrypt the file, and export and output
        with open(_gp.decrypt(args.command[1], args.command[2]), 'w') as export:
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
            with open(consts.PICKLE_CONTEXT, 'r') as context:
                cgp = pickle.load(context)
                if cgp.uuid == args.command[1]:
                    raise ghostpass.GhostpassException("session is currently open. Please close before destructing")

        # explicitly get user permission, and delete the session
        yn = raw_input("\n> Are you sure you want to delete this session? (y / n) ")
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
