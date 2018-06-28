'''
    crypto.py
        Interface for crytographic operations, including AES and our custom Markov-chained cipher
'''

import re
import hashlib
import base64

from Crypto import Random
from Crypto.Cipher import AES

MARKOV_START = "<START>"
MIN_LINE_LEN = 4

class MarkovHelper:

    def __init__(self, model, inputstate=2):

        self.model = open(model, 'r').read() # read the model as a list of chars
        self.bigrams = []

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
    def repeats(words):
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
    def mlower(word):
        if word != MARKOV_START:
            return word.lower()
        else:
            return word


    def make_lower(self, word):
        '''
        lowers all the words within a list or tuple except for the MARKOV_START token
        '''

    	if type(word) is list:
    		return [self.mlower(w) for w in word]
    	elif type(word) is tuple:
    		return tuple([self.mlower(w) for w in word])

        return self.mlower(word)


    def add_bigram(self, word1, word2):
    	word1b = self.make_lower(word1)

    	if word1b in self.bigramsDict:
    		(w1, w2) = self.bigramsDict[word1b]
    		w2.append(word2)
    	else:
    		self.bigramsDict[word1b] = (word1, [word2])


    def compute_probabilities(self, words):
    	'''
        given a list of words, compute the probability (in a fraction) for each word
        '''

        # check for repeats in a set of words
    	count = self.repeats(words)

    	total = sum([c[1] for c in count])
        return [(c[0], (c[1], total)) for c in count]


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
    			self.add_bigram((bigram[0], bigram[1]), bigram[2])

        # at this point, fullBigrams contains the markovChain with probabilities in fractions
    	fullBigrams = self.bigramsDict.values()
    	self.bigrams = [(bigram[0], self.compute_probabilities(bigram[1])) for bigram in fullBigrams]


    def generate_text(self):

        self.words = []
        prev = MARKOV_START

        markovDict = {}
        for bigram in self.bigrams:
            markovDict[self.make_lower(self.toTuple(bigram[0]))] = bigram[1]

        while True:
            m = markovDict(self.make_lower(prev))
            denominator = m[0][1][1]
            rnd = random.randint(1, denominator)
            total = 0
            nextWord = None

            for word in m:
                total = total + word[1][0]
                if total >= rnd:
                    nextWord = word[0]
                    break

            if nextWord == MARKOV_START:
                break

            self.words.append(nextWord)

            prev = (prev[1], nextWord)



class AESHelper:

    # TODO: documentation for this whole class

    def __init__(self, key):
        self.keysize = 32 # represents 32 byte-sized key
        self.key = key    # key has already been converted into SHA256 hash in ghostpass object


    def aes_encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))


    def aes_decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')


    def _pad(self, s):
        return s + (self.keysize - len(s) % self.keysize) * chr(self.keysize - len(s) % self.keysize)


    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]
