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


class MarkovHelper:
    """
    The MarkovHelper class provides an interface to several methods that enable for the creation of a
    Markov chain model, and enable encryption / decryption through the specified corpus. These methods
    were largely based off of Dr. H. Moraldo's Markov textual steganography research, specified here:
    https://github.com/hmoraldo/markovTextStego
    """

    def __init__(self, corpus):
        self.corpus = corpus
        self.bigrams = []


    def _compute_probabilities(self, words):
        """
        computes the number of repeats within a corpus, and calculates
        probability of the next word showing up.
        """
        count = utils.count_repeats(words)
        total = sum([c[1] for c in count])
        return [(c[0], (c[1], total)) for c in count]


    def init_mc(self):
        """
        initialize a Markov-chained model for generating plaintext-like
        ciphertext. This is used for both encryption AND decryption.
        """

        # break specified corpus into lines using regex
        lines = [re.findall(r"\w[\w']*", line) for line
                in re.split(r"\r\n\r\n|\n\n|\,|\.|\!", self.corpus)]
        lines = [[consts.MARKOV_START] + line + [consts.MARKOV_START] for line
                in lines if len(line) >= consts.MIN_LINE_LEN]

        # initialize bigrams from words in lines
        bigrams = [[(line[word], line[word + 1]) for word in range(len(line) - 1)] for line in lines]

        bigrams_dict = {}

        for line in bigrams:
            for bigram in line:
                
                word = utils.word_lower(bigram[0])

                if word in bigrams_dict:
                    (w1, w2) = bigrams_dict[word]
                    w2.append(bigram[1])
                else:
                    bigrams_dict[word] = (word, [bigram[1]])

        full_bigrams = bigrams_dict.values()
        full_bigrams = [(bigram[0], self._compute_probabilities(bigram[1])) for bigram in full_bigrams]

        # delete the final document key
        del self.corpus

        self.bigrams = full_bigrams


    # TODO: implement
    def encrypt_text(self, cleartext):
        return 0


    # TODO: implement
    def decrypt_text(self, ciphertext):
        return 0





class AESHelper:
    """
    AESHelper is a class that provides an interface for AES-CBC
    encryption and decryption. While the Ghostpass protocol does not
    require the use of AES, we utilize it in this reference implementation
    to show the plugability of other cryptographic protocols. AES in this
    context is used to encrypt fields.
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
