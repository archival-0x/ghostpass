'''
    consts.py
        core interface for interacting with Ghostpass
'''
import names
import random
import hashlib
import json
import jsonpickle

import crypto
import consts

from consts import Color as color

# Define an exception that inherits Exception
class GhostpassException(Exception):
    def __init__(self, message):
        print color.R + "[!] Error: " + message + color.W
        exit(1)


class Ghostpass(object):

    # represents global pseudorandom identifying ID for session
    uuid = names.get_first_name() + names.get_first_name() + str(random.randrange(0, 100))


    ############################################################
    # Standard methods
    #   - initializes Ghostpass context and enables writing to
    #   session for portable reuse
    ############################################################


    def __init__(self):
        '''
        initializes the state of the instance variables we need
        '''

        self.uuid = self.uuid   # for de/serialization purposes
        self.password = None    # represents master password (SHA512 encrypted)
        self.data = []          # used to store key-value entries, AES encrypted with master password
        # TODO: timestamp?? mutex lock??


    def __repr__(self):
        return "Ghostpass - {}: {}".format(self.uuid, json.dumps(self.__dict__))


    def init_state(self, password):
        '''
        initializes the new session, immediately hashing the master password
        '''

        # perform error-checking and hash using SHA512
        if password == "":
            raise GhostpassException("master password is not optional")
        self.password = hashlib.sha512(password).hexdigest()

        # since cleartext password is copied to object, make sure to delete
        del password

        return 0


    def load_corpus(self, corpus_path):
        '''
        load corpus file when doing actual encryption/decryption
        '''

        # ensure that path is not empty: corpus is not optional
        if corpus_path == "":
            raise GhostpassException("corpus path is not optional")

        # convert path into Markov-chain cipher and generate markov chain cipher
        self.markov = crypto.MarkovHelper(corpus_path)
        self.markov.add_text()

        return 0


    def export(self):
        '''
        using jsonpickle, create a new session file that stores the specific session data.
        the user can then re-open and "import" the object for further use and overwrite
        '''

        # Export to new JSON file
        with open(consts.DEFAULT_CONFIG_PATH + "/" + self.uuid, "w+") as f:
            f.write(jsonpickle.encode(self))
        return 0

    ############################################################
    # Secret handling methods
    #   - performs the actual mutation of self.data, which stores
    #   all of the important and sensitive fields and secrets
    #   (i.e username and password combos)
    ############################################################

    @staticmethod
    def _check_field_existence(field):
        # TODO: fast self.data check
        return True


    def view_field(self, field, password):
        return 0


    def add_field(self, field, password):
        '''
        securely add field with password to self.data, encrypting with AES immediately before commit
        '''

        # ensure that secret is not empty: secret is not optional
        if password == "":
            raise GhostpassException("no secret specified for field: {}".format(field))

        return 0


    def remove_field(self, field):
        return 0


    def stash_changes(self):
        return 0


    ############################################################
    # Crypto handlers
    #    - perform session-less or session-dependent encryption
    #    or decryption. Note that results are always text files
    ############################################################


    def encrypt(self):

        # TODO: use AES with masterpassword to encrypt all data in pickle
        #       markov chain cipher
        #       return ciphertext
        return 0


    def decrypt(self):

        # TODO: markov chain cipher
        #       use AES with masterpassword to decrypt all data in ciphertext
        #       return cleartext
        return 0
