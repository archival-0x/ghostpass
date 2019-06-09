"""
ghostpass.py

    Core interface for interacting with the Ghostpass protocol. CLI directly
    interacts with a ghostpass.Ghostpass() object in order to keep and change state.
    Calls upon crypto and Markov chain helpers in order to perform encryption/decryption/

"""
import random
import json
import jsonpickle
import names
import hashlib
import threading
import tabulate

from . import crypto
from . import consts
from .consts import Color as color


class GhostpassException(Exception):
    """ defines custom Ghostpass exception """
    def __init__(self, message):
        print(color.R + "[!] Error: " + message + color.W)
        exit(1)


# create a global mutex lock for critical sections
global_mutex = threading.Lock()


class Ghostpass(object):

    # represents global pseudorandom identifying ID for session
    uuid = names.get_first_name() + names.get_first_name() + str(random.randrange(0, 100))

    def __init__(self):
        self.uuid = self.uuid
        self.password = None
        self.encrypted = False
        self.data = []


    def __repr__(self):
        return "Ghostpass - {}: {}".format(self.uuid, json.dumps(self.__dict__))


    def init_state(self, password, corpus):
        """
        initializes the new session, immediately hashing the master password such
        that runtime doesn't expose cleartext
        """
        if password == "" or password == None:
            raise GhostpassException("master password is not optional")
        if corpus == "" or corpus == None:
            raise GhostpassException("corpus path is not optional")

        # store hash and initialize crypto helper
        self.password = hashlib.sha512(password.encode('utf-8')).hexdigest()
        self.aeshelp = crypto.AESHelper(self.password)

        # open and store initial document key as list
        with open(corpus, 'r') as corpus_file:
            initial_doc = corpus_file.readlines()

        # initialize Markov object with corpus
        self.model = crypto.MarkovHelper(corpus)
        self.model.init_mc()

        # since cleartext password is copied to object, make sure to delete
        del password


    def export(self):
        """
        using jsonpickle, create a new session file that stores the specific session data.
        the user can then re-open and "import" the object for further use and overwrite
        """
        with open(consts.DEFAULT_CONFIG_PATH + "/" + self.uuid, "w+") as f:
            f.write(jsonpickle.encode(self))


    def _check_field_existence(self, field):
        """
        check to see if the specified field already exists in
        our set of data
        """
        for f in self.data:
            for k, v in f.iteritems():
                if k == field:
                    return True
        return False


    def view_field(self, field):
        """
        returns the unencrypted version of secret of a specific field.
        """
        if not self._check_field_existence(field):
            raise GhostpassException("field {} doesn't exist!".format(field))

        # search through self.data for specific field that matches key
        # then it is appended to a list and then formatted for pretty-print
        entry = [[key, value[0], value[1]]
            for f in self.data
            for key, value in f.iteritems()
            if key == field
        ]
        return tabulate.tabulate(entry, headers=["Field", "Username", "Password"])


    def view_all(self):
        """
        returns a pretty-printed grid formatted table of all unencrypted secrets
        """
        table = [[key, value[0], value[1]]
                for key, value in field.iteritems()
                for field in self.data
        ]
        return tabulate.tabulate(table, headers=["Field", "Username", "Password"])


    def add_field(self, field, username, password):
        """
        add field with password to self.data if not exist, without any encryption done.
        """
        if self._check_field_existence(field):
            raise GhostpassException("field {} already exists!".format(field))

        global_mutex.acquire()
        try:
            self.data.append({field: (username, password) })
        except Exception:
            return 1
        finally:
            global_mutex.release()


    def remove_field(self, field):
        """
        removes field from self.data if exists
        """
        if not self._check_field_existence(field):
            raise GhostpassException("field {} doesn't exist!".format(field))

        global_mutex.acquire()
        try:
            self.data = [f for f in self.data if str(field) not in f]
        except Exception:
            return 1
        finally:
            global_mutex.release()


    def overwrite_field(self, field, username, password):
        """
        change specified field with new secret
        """
        if not self._check_field_existence(field):
            raise GhostpassException("field {} doesn't exist!".format(field))

        global_mutex.acquire()
        try:
            self.data[field] = (username, password)
        except Exception:
            return 1
        finally:
            global_mutex.release()


    def encrypt_fields(self):
        """
        encrypt each field using AES-CBC. Set encrypted flag to true
        """
        self.data = [(self.aeshelp.encrypt(value[0]), self.aeshelp.encrypt(value[1]))
            for f in self.data
            for key, value in f.iteritems()
        ]
        self.encrypted = True


    def decrypt_fields(self):
        """
        decrypt each field using AES-CBC. Set encrypted flag to false
        """
        self.data = [(self.aeshelp.decrypt(value[0]), self.aeshelp.decrypt(value[1]))
            for f in self.data
            for key, value in f.iteritems()
        ]
        self.encrypted = False


    def encode_file(self):
        """
        apply Markov chained cipher to create a ciphertext out of a specified raw textfile
        """
        self.model.encrypt_text()


    def decode_file(self, ciphertext):
        """
        works independently - decrypt with specified corpus file, then decrypt with
        AES-CBC, then export cleartext as .txt file
        """
        return 0
