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

    def __init__(self):
        '''
        initializes the state of the instance variables we need
        '''

        self.uuid = self.uuid   # for de/serialization purposes
        self.password = None    # represents master password (SHA512 encrypted)
        self.data = []          # used to store key-value entries, AES encrypted with master password
        # TODO: timestamp


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

        # convert path into Markov-chain cipher
        if corpus_path == "":
            raise GhostpassException("corpus path is not optional")

        # generate markov chain cipher
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
