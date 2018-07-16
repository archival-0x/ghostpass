'''
    utils.py
        Helper functions, mostly for text manipulation
'''

import re

import consts

def _word_lower(word):
    '''
    lowers a word if not the MARKOV_START symbol
    '''
    if word != consts.MARKOV_START:
        return word.lower()
    else:
        return word


def _make_lower(word):
    '''
    lowers all the words within a list or tuple except for the MARKOV_START token
    '''

    if type(word) is list:
		return [_word_lower(w) for w in word]
    elif type(word) is tuple:
		return tuple([_word_lower(w) for w in word])

    return _word_lower(word)


def _count_repeats(words):
    '''
    helper - given a list of words, count how many times each one is listed
    '''

    # create a dict to store counts of word in corpus
    count = {}

    # for each word in the the list of words
    for word in words:

        # our model is case-insensitive, so lower
        w = word.lower()

        # add to dict, and increment if word is repeated
        if w in count:
			count[w] = (word, count[w][1] + 1)
        else:
			count[w] = (word, 1)

    return count.values()


def _to_tuple(t):
    '''
    helper - given a variable, determine type and return as tuple
    '''

    if type(t) == list:
        return tuple(t)
    else:
        return t
