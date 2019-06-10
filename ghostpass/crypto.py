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
        count = utils._count_repeats(words)
        total = sum([c[1] for c in count])
        return [(c[0], (c[1], total)) for c in count]


    def init_mc(self):
        """
        initialize a Markov-chained model for generating plaintext-like
        ciphertext. This is used for both encryption AND decryption.
        """

        # break specified corpus into lines using regex
        lines = [line.rstrip('\n') for line in self.corpus]

        # append the MARKOV_START symbol for lines with longer than 4 words
        for i, line in enumerate(lines):
            if len(line) >= consts.MIN_LINE_LEN:
                lines[i] = [consts.MARKOV_START + line + consts.MARKOV_START]

        # generate our bigrams in the style of a list
        bigrams1 = [[(line[word], line[word + 1], line[word + 2]) for word in range(len(line) - 2)] for line in lines]
        bigrams2 = [[(line[0], line[0], line[1])] for line in lines]
        bigrams = bigrams1 + bigrams2

        bigramsDict = {}
        for line in bigrams:
            for bigram in line:

                # where the first element is the input state, with two works (hence BIgram)
                word1 = (bigram[0], bigram[1])

                # ensure that word is subject to case-insensitivity
                inputState = utils._make_lower(word1)
                outputState = bigram[2]

                # check if our dict already contains the inputState, update by adding an output state
                if inputState in bigramsDict:
                    (w1, w2) = bigramsDict[inputState]
                    w2.append(outputState)
                else:
                    bigramsDict[inputState] = (word1, [outputState])

        # at this point, fullBigrams contains the markovChain with probabilities in fractions
        fullBigrams = bigramsDict.values()

        # create final model with probability of next transition state
        for bigram in fullBigrams:
            self.bigrams.append((bigram[0], self._compute_probabilities(bigram[1])))

        # delete the final document key
        del self.corpus


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
