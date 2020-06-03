"""
crypto.py

  Module for ghostpass for relevant cryptographic operations. This includes
  an object for generating a Markov chain based on a defined corpus, and an
  AES object for encrypting and decrypting given input and a hash.

"""
import re
import hashlib
import random
import base64
import math
import binascii

from Crypto import Random
from Crypto.Cipher import AES

from . import utils
from . import consts


class Markov:
    """
    The Markov class provides an interface to several methods that enable for the creation of a Markov chain model, which
    contains the list of nodes, their frequency counts and probabilities after extracting n-grams given a corpus file
    """

    def __init__(self, corpus):
        """
        initialize a Markov-chained model for generating plaintext-like
        ciphertext. This is used for both encryption AND decryption.
        """

        # delete the document key
        del corpus


    def _compute_probabilities(self, words):
        """
        computes the number of repeats within a corpus, and calculates
        probability of the next word showing up.
        """
        count = utils.count_repeats(words)
        total = sum([c[1] for c in count])
        return [(c[0], (c[1], total)) for c in count]


    # TODO: implement
    def encrypt_text(self, cleartext):
        bytelist = self.convert_to_bytelist(len(cleartext), 2)
        bitsfield = BitField(bytelist)

        bitsfield = BitField(data)



    # TODO: implement
    def decrypt_text(self, ciphertext):
        return 0



class AESHelper:
    """
    AESHelper is an interface that provides an interface for AES-CBC
    encryption and decryption.

    While the Ghostpass protocol does not require the use of AES, we utilize it in this reference
    implementation to show the plugability of other cryptographic protocols. AES in this context is
    used to encrypt fields.
    """

    def __init__(self, key):
        self.blocksize = 64
        self.key = key


    def _pad(self, s):
        return s + (self.blocksize - len(s) % self.blocksize) * chr(self.blocksize - len(s) % self.blocksize)


    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


    def encrypt(self, raw):
        """
        encrypt raw text into an encrypted AES ciphertext
        """
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))


    def decrypt(self, enc):
        """
        decrypt encoded text into an raw text
        """
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')
