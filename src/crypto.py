'''
    consts.py
        Interface for our Markov-chained cipher
'''

from bitstring import BitArray, ConstBitArray

class MarkovHelper:

    def __init__(self, model, context=3):

        self.model = open(model, 'r').read() # read the model as a list of chars
        self.context = context # order of reading

        self._children = [0, {}, None]
        self.current_token = None
        self.pointer = self._children


    def add_text(self):
        '''
        initialize a model for a language-based cipher
        '''
        phrases = self.to_phrases(self.context, self.to_words(self.model))
        for p in phrases:
            self.add_phrase(p)
        self.update_root_count()


    def add_phrase(self, p):
        ptr = self._children[1]
        for token in p:
            if token not in ptr:
               ptr[token] = [0, {}, None]

            ptr[token][0] += 1
        ptr = ptr[token][1]


    def update_root_count(self):
        tokens = self._children[1].values()
        total = sum(map(lambda t: t[0], tokens))
        self._children[0] = total


    @staticmethod
    def to_phrases(order, words):
        return [tuple([words[i+j] for j in xrange(order+1)])
            for i in xrange(len(words) - order)]


    @staticmethod
    def to_words(text):
        return text.split()
