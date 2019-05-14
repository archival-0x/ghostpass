"""
    crypto.py
        Interface for crytographic operations, including AES and our custom Markov-chained cipher
"""
import re
import hashlib
import random
import base64
import math
import binascii

from Crypto import Random
from Crypto.Cipher import AES

import ghostpass.utils as utils
import ghostpass.consts as consts


class MarkovHelper:
    """
    <Purpose>
      The MarkovHelper class provides an interface to several methods that enable for the creation of a
      Markov chain model, and enable encryption / decryption through the specified corpus. These methods
      were largely based off of Dr. H. Moraldo's Markov textual steganography research, specified here:
      https://github.com/hmoraldo/markovTextStego
    """

    def __init__(self, initial_corpus):
        self.initial_corpus = initial_corpus  # stores list of words from initial corpus
        self.bigrams = []                     # stores bigram tuples for Markov Chain


    def _compute_probabilities(self, words):
        """
        <Purpose>
          This method is core for the Markov chain generation process, as it first computes the number
          of repeats within a corpus, and calculating the probability of the next work showing up.

        <Returns>
          List of words

        """
        count = utils._count_repeats(words)
        total = sum([c[1] for c in count])
        return [(c[0], (c[1], total)) for c in count]



    def generate_key(self, hashpwd):
        """
        <Purpose>
          This method takes an initial document key, and a SHA512 hash, and performs
          the first round key-derivation function that produces a final document key.
          Our hash is converted into a binary bit array (8-bits per bitstring), and
          bit expansion with a factor of 3 is applied. The final expanded bit array
          is converted to decimal, and used to determine positions in the initial wordlist.
          A final wordlist of all those positions are set as the final document key.

        <Returns>
          None

        """

        # hashstring into a decimal list
        raw_str = binascii.unhexlify(hashpwd)
        dec_array = [ord(x) for x in raw_str]

        # expand our list using an expansion factor of 3
        expanded_array = []
        for dec in dec_array:
            lut_val = consts.EXPANSION_TABLE[dec]
            expanded_array.append(lut_val >> 16)
            expanded_array.append(lut_val >> 8)
            expanded_array.append(lut_val)


        # generate our final document key
        self.corpus = []
        for i, value in enumerate(self.initial_corpus):
            for dec in expanded_array:
                if i == dec:
                    self.corpus.append(self.initial_corpus[dec])

        # convert corpus into a string
        self.corpus = "".join(self.corpus)
        del self.initial_corpus



    def init_mc(self):
        '''
        initialize a Markov-chained model for generating plaintext-like
        ciphertext. This is used for both encryption AND decryption.
        '''

        # break specified corpus into lines using regex
        lines = [re.findall(r"\w[\w']*", line) for line
                 in re.split(r"\r\n\r\n|\n\n|\,|\.|\!", self.corpus)]

        # append the MARKOV_START symbol for lines with longer than 4 words
        for line in lines:
            if len(line) >= consts.MIN_LINE_LEN:
                lines = [[consts.MARKOV_START] + line + [consts.MARKOV_START]]

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


    def encrypt_text(self, cleartext):
        return 0


    def decrypt_text(self, ciphertext):
        return 0





class AESHelper:
    """
    <Purpose>
      AESHelper is a class that provides an interface for AES-CBC
      encryption and decryption. While the Ghostpass protocol does not
      require the use of AES, we utilize it in this reference implementation
      to show the plugability of other cryptographic protocols. AES in this
      context is used to encrypt fields.
    """

    def __init__(self, key):
        self.blocksize = 64     # represents 32 byte-sized key
        self.key = key          # key has already been converted into SHA512 hash in ghostpass object


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


    def _pad(self, s):
        return s + (self.blocksize - len(s) % self.blocksize) * chr(self.blocksize - len(s) % self.blocksize)


    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]
