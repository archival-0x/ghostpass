'''
    ghostpass.py
        core interface for interacting with Ghostpass
'''
import names
import random
import hashlib
import json
import jsonpickle
import threading

import crypto
import consts

from consts import Color as color

# Define a custom exception
class GhostpassException(Exception):
    def __init__(self, message):
        print color.R + "[!] Error: " + message + color.W
        exit(1)

global_mutex = threading.Lock()   # create a mutex lock for when working with data

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

        # TODO: Timestamp? Flag for open / closed ?
        self.uuid = self.uuid           # for de/serialization purposes
        self.password = None            # represents master password (SHA256 encrypted)
        self.data = []                  # used to store key-value entries, AES encrypted with master password


    def __repr__(self):
        return "Ghostpass - {}: {}".format(self.uuid, json.dumps(self.__dict__))


    def init_state(self, password):
        '''
        initializes the new session, immediately hashing the master password such
        that runtime doesn't expose cleartext
        '''

        # perform error-checking and hash using SHA256
        if password == "":
            raise GhostpassException("master password is not optional")
        self.password = hashlib.sha256(password).hexdigest()

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
        self.markov.init_mc()

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

    def _check_field_existence(self, field):
        '''
        using any(), check to see if the specified field already exists in
        our set of data
        '''

        # TODO: was lazy, MAKE MORE FUNCTIONAL AND EFFICIENT!
        for f in self.data:
            for k, v in f.iteritems():
                if k == field:
                    return True

        return False


    def view_field(self, field, password):
        return 0


    def view_all(self):
        # TODO: make it look nice!
        return self.data


    def add_field(self, field, username, password):
        '''
        add field with password to self.data if not exist, without any encryption done.
        '''

        # check if field exists, and throw back error
        if self._check_field_existence(field):
            raise GhostpassException("field {} already exists!".format(field))

        # critical section, mutex lock
        global_mutex.acquire()
        try:
            self.data.append({field: (username, password) })
        except Exception:
            return 1
        finally:
            global_mutex.release()

        return 0


    def remove_field(self, field):
        '''
        removes field from self.data if exists
        '''

        # check if field doesn't exist, and throw back error
        if not self._check_field_existence(field):
            raise GhostpassException("field {} doesn't exist!".format(field))

        # critical section, mutex lock
        global_mutex.acquire()
        try:
            self.data = [f for f in self.data if str(field) not in f]
        except Exception:
            return 1
        finally:
            global_mutex.release()

        return 0


    def overwrite_field(self, field, username, password):

        # check if field doesn't exist, and throw back error
        if not self._check_field_existence(field):
            raise GhostpassException("field {} doesn't exist!".format(field))

        global_mutex.acquire()
        try:
            self.data[field] = (username, password)
        finally:
            global_mutex.release()


    def stash_changes(self):
        '''
        encrypt fields with AES-CBC, and move changes from context into original
        JSON
        '''
        return 0


    ############################################################
    # Crypto handlers
    #    - perform session-less or session-dependent encryption
    #    or decryption. Note that results are always text files
    ############################################################


    def encrypt(self):
        '''
        encrypt fields in self.data with AES-CBC, then our Markov-chain cipher,
        then export it as a .txt file
        '''
        return 0


    def encrypt_file(self, file):
        '''
        encrypt cleartext file with AES-CBC, then our Markov-chain cipher,
        then export it as a .txt file
        '''
        return 0


    def decrypt(ciphertext, corpus):
        '''
        works independently - decrypt with specified corpus fle, then decrypt with
        AES-CBC, then export cleartext as .txt file
        '''
        return 0
