'''
    consts.py
        Interface for our Markov-chained cipher
'''

import re

MARKOV_START = "<START>"
MIN_LINE_LEN = 4

class MarkovHelper:

    def __init__(self, model, inputstate=2):

        self.model = open(model, 'r').read() # read the model as a list of chars
        self.inputstate = inputstate         # where 2 = create bigrams

        self.bigrams = []


    @staticmethod
    def repeats(words):
        '''
        given a list of words, count how many times each one is listed
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
        if w != MARKOV_START:
            return w.lower()
        else:
            return w


    @staticmethod
    def make_lower(word):
        '''
        lowers all the words within a list or tuple except for the MARKOV_START token
        '''

    	if type(word) is list:
    		return [self.mlower(w) for w in word]
    	elif type(word) is tuple:
    		return tuple([self.mlower(w) for w in word])

        return self.mlower(word)


    @staticmethod
    def add_bigram(word1, word2):
    	word1b = self.make_lower(word1)

    	if word1b in self.bigramsDict:
    		(w1, w2) = self.bigramsDict[word1b]
    		w2.append(word2)
    	else:
    		self.bigramsDict[word1b] = (word1, [word2])


    @staticmethod
    def compute_probabilities(words):
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

        # split sentences, get bigrams
    	lines = [re.findall(r"\w[\w']*", line) for line
    		in re.split(r"\r\n\r\n|\n\n|\,|\.|\!", self.model)]
    	lines = [[MARKOV_START] + line + [MARKOV_START] for line
    		in lines if len(line) >= MIN_LINE_LEN]

        # create bigrams
    	bigrams1 = [[(line[word], line[word+1], line[word+2]) for word in range(len(line)-2)] for line in lines]
    	bigrams2 = [[(line[0], line[0], line[1])] for line in lines]
    	bigrams = bigrams1 + bigrams2

    	# compute markov chain
    	# in this context, we call bigrams the pairs (input state, output state); not the best name
    	# when the input state has more than 1 word unfortunately
    	self.bigramsDict = {}

    	for line in bigrams:
    		for bigram in line:
    			if wordsPerState == 1:
    				self.add_bigram(bigram[0], bigram[1])
    			elif wordsPerState == 2:
    				self.add_bigram((bigram[0], bigram[1]), bigram[2])

        # at this point, fullBigrams contains the markovChain with probabilities in fractions
    	fullBigrams = bigramsDict.values()
    	self.bigrams = [(bigram[0], self.compute_probabilities(bigram[1])) for bigram in fullBigrams]
