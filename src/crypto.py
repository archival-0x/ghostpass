'''
    crypto.py
        Interface for crytographic operations, including AES and our custom Markov-chained cipher
'''

import re
import hashlib
import random
import base64

from Crypto import Random
from Crypto.Cipher import AES

MARKOV_START = "<START>"
MIN_LINE_LEN = 4

class MarkovHelper:

    def __init__(self, model, inputstate=2):

        self.model = open(model, 'r').read() # read the model as a list of chars
        self.bigrams = []                    # stores bigram tuples for Markov Chain


    ####################################
    # Text manipulation helper functions
    ####################################


    @staticmethod
    def toTuple(t):
        '''
        helper - given a variable, determine type and return as tuple
        '''

        if type(t) == list:
            return tuple(t)
        else:
            return t


    @staticmethod
    def _repeats(words):
        '''
        helper - given a list of words, count how many times each one is listed
        '''

        # create a dict to store counts of word in corpus
    	count = {}

    	for word in words:
            # case-insensitive check
            w = word.lower()

            # add to dict, and increment if word is repeated
    	    if w in count:
    			count[w] = (word, count[w][1] + 1)
    	    else:
    			count[w] = (word, 1)

        return count.values()


    @staticmethod
    def _word_lower(word):
        '''
        lowers a word if not the MARKOV_START symbol
        '''
        if word != MARKOV_START:
            return word.lower()
        else:
            return word


    def _make_lower(self, word):
        '''
        lowers all the words within a list or tuple except for the MARKOV_START token
        '''

    	if type(word) is list:
    		return [self._word_lower(w) for w in word]
    	elif type(word) is tuple:
    		return tuple([self._word_lower(w) for w in word])

        return self._word_lower(word)


    def _add_bigram(self, word1, word2):
        '''
        creates a bigram and appends to self.bigramsDict
        '''

    	word1b = self._make_lower(word1)

    	if word1b in self.bigramsDict:
    		(w1, w2) = self.bigramsDict[word1b]
    		w2.append(word2)
    	else:
    		self.bigramsDict[word1b] = (word1, [word2])


    @staticmethod
    def _list_to_text(str1):
        '''
        convert a list of words into text
        '''

    	text = ""
    	lastWord = config.startSymbol

    	for word in strl:
    		if lastWord == config.startSymbol and word != config.startSymbol:
    			word = word[0].capitalize() + word[1:]

    		if word != config.startSymbol and text != "":
    			text = text + " "

    		if not(text == "" and word == config.startSymbol):
    			if word == config.startSymbol:
    				text = text + "."
    			else:
    				text = text + word

    		lastWord = word

        return text.rstrip("")


    def _compute_probabilities(self, words):
    	'''
        given a list of words, compute the probability (in a fraction) for each word
        '''

        # check for repeats in a set of words
    	count = self._repeats(words)

    	total = sum([c[1] for c in count])
        return [(c[0], (c[1], total)) for c in count]


    ####################################
    # Actual interface functions
    ####################################


    def init_mc(self):
        '''
        initialize a new Markov-chained cipher
        '''

        # break specified corpus into lines using regex
    	lines = [re.findall(r"\w[\w']*", line) for line
    		in re.split(r"\r\n\r\n|\n\n|\,|\.|\!", self.model)]

        # append the MARKOV_START symbol for parsing purposes
    	lines = [[MARKOV_START] + line + [MARKOV_START] for line
    		in lines if len(line) >= MIN_LINE_LEN]

        # create our bigrams
    	bigrams1 = [[(line[word], line[word+1], line[word+2]) for word in range(len(line) - 2)] for line in lines]
    	bigrams2 = [[(line[0], line[0], line[1])] for line in lines]
    	bigrams = bigrams1 + bigrams2

    	# compute markov chain
    	# in this context, we call bigrams the pairs (input state, output state); not the best name
    	# when the input state has more than 1 word unfortunately
    	self.bigramsDict = {}

    	for line in bigrams:
    		for bigram in line:
    			self._add_bigram((bigram[0], bigram[1]), bigram[2])

        # at this point, fullBigrams contains the markovChain with probabilities in fractions
    	fullBigrams = self.bigramsDict.values()
    	self.bigrams = [(bigram[0], self._compute_probabilities(bigram[1])) for bigram in fullBigrams]


    def generate_text(self):
        '''
        generate actual text from markov chain cipher, and returns text as a list
        '''

        # create a list to store generated text
        words = []
        prev = MARKOV_START

        markovDict = {}
        for bigram in self.bigrams:
            markovDict[self._make_lower(self.toTuple(bigram[0]))] = bigram[1]

        while True:
            m = markovDict(self._make_lower(prev))
            denominator = m[0][1][1]
            rnd = random.randint(1, denominator)
            total = 0
            nextWord = None

            for word in m:
                total = total + word[1][0]
                if total >= rnd:
                    nextWord = word[0]
                    break

            # check if MARKOV_START is the next word
            if nextWord == MARKOV_START:
                break

            # add words into list
            words.append(nextWord)

            prev = (prev[1], nextWord)

        # return words, converted as text
        return self._list_to_text(words)


    def decrypt_text(self, ciphertext):
        '''
        decrypts the ciphertext, using Markov chain cipher
        '''

        return 0


class AESHelper:

    def __init__(self, key):
        self.blocksize = 32 # represents 16 byte-sized key
        self.key = key    # key has already been converted into SHA256 hash in ghostpass object


    def encrypt(self, raw):
        '''
        encrypt raw text into an encrypted AES ciphertext
        '''
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))


    def decrypt(self, enc):
        '''
        decrypt encoded text into an raw text
        '''
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')


    def _pad(self, s):
        return s + (self.blocksize - len(s) % self.blocksize) * chr(self.blocksize - len(s) % self.blocksize)


    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]
