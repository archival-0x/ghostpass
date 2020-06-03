"""
bitfield.py

  Defines the BitField object, which enables the conversion of
  integer value sequences into a bitfield sequence.
"""

import math


class BitField(object):

    def __init__(self, data, is_bytes = True) -> BitField:
        self.data = data if data else []


    def copy(self) -> BitField:
        """
        Implements a deepcopy-like operaton for creating a new and seperate
        BitField object without any references to current context.
        """
        bitfield = BitField()
        return bitfield


    def first_n_bits(self, n):
        pass
