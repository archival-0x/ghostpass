"""
    utils.py
        Helper functions, mostly for text manipulation
"""
import re
import ghostpass.consts as consts


def _word_lower(word):
    """
    lowers a word if not the MARKOV_START symbol
    """
    if word != consts.MARKOV_START:
        return word.lower()
    else:
        return word


def _make_lower(word):
    """
    lowers all the words within a list or tuple except for
    the MARKOV_START token
    """
    if type(word) is list:
        return [_word_lower(w) for w in word]
    elif type(word) is tuple:
        return tuple([_word_lower(w) for w in word])
    return _word_lower(word)


def _count_repeats(words):
    """
    given a list of words, count how many times each one is listed
    """
    count = {}
    for word in words:
        w = word.lower()
        if w in count:
            count[w] = (word, count[w][1] + 1)
        else:
            count[w] = (word, 1)
    return count.values()


def _to_tuple(t):
    """
    helper - given a variable, determine type and return as tuple
    """
    if type(t) == list:
        return tuple(t)
    else:
        return t
