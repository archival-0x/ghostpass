import utils
import math

"""
a class for managing big amounts of bits (these bits are internally stored as bytes, except in the left and right extremes)
"""
class BigBitField:

    def __init__(self, data = None, dataIsBytes = True):
        if data is None:
            data = []

        self.lastBitsCache = ""

        if dataIsBytes:
            self.firstBitsCache = ""
            self.remainingBytes = data
        else:
            self.firstBitsCache = data
            self.remainingBytes = []


    def copy(self):
        bitField = BigBitField()
        bitField.firstBitsCache = self.firstBitsCache
        bitField.lastBitsCache = self.lastBitsCache
        bitField.remainingBytes = list(self.remainingBytes)
        return bitField

    """
    internal; we store data as bytes and as a string with the explicit bits... this function extracts n bytes into the
    string, and converts them to ascii 1 and 0 that is easy to operate with
    """
    def popBytesToBitsCache(self, bytesToPop):
        if len(self.remainingBytes) < bytesToPop:
            raise RuntimeError("not enough bytes for popToBits operation")

        for x in range(bytesToPop):
            byte = self.remainingBytes.pop(0)
            bits = utils.toBinary(byte, 8)
            self.firstBitsCache = self.firstBitsCache + bits

    def totalFieldLen(self):
        return len(self.firstBitsCache) + len(self.remainingBytes) * 8 + len(self.lastBitsCache)


    "internal: gets at least n bits extra ready in firstBitsCache"
    def getNBitsReady(self, bitsCount):
        if self.totalFieldLen() < bitsCount:
            raise RuntimeError("not enough bits for getNBitsReady")
        else:
            while len(self.firstBitsCache) < bitsCount:
                # push bytes to bits
                bytesToGet = int(math.ceil((bitsCount - len(self.firstBitsCache)) / 8.0))
                bytesToGet = min(len(self.remainingBytes), bytesToGet)
                self.popBytesToBitsCache(bytesToGet)

                # if no more bytes, move all bits from one extreme to the other
                # (even if this means getting more bits ready than what the user asked for)
                if self.remainingBytes == []:
                    self.firstBitsCache = self.firstBitsCache + self.lastBitsCache
                    self.lastBitsCache = ""

    "get n bits from the field, but don't change the field"
    def getFirstNBits(self, bitsCount):
        self.getNBitsReady(bitsCount)

        return self.firstBitsCache[0:bitsCount]

    "pop the first n bits from the field"
    def popFirstNBits(self, bitsCount):
        self.getNBitsReady(bitsCount)
        firstNBits = self.firstBitsCache[0:bitsCount]
        self.firstBitsCache = self.firstBitsCache[bitsCount:]

        return firstNBits

    "push a number of bits, as in a stack (from the top or first bits)"
    def pushNBits(self, bits):
        self.firstBitsCache = bits + self.firstBitsCache
        while len(self.firstBitsCache) >= 8:
            idx = len(self.firstBitsCache) - 8
            self.remainingBytes.insert(0, utils.fromBinary(self.firstBitsCache[idx:]))
            self.firstBitsCache = self.firstBitsCache[0:idx]

    "push a number of bits, as in a queue (from the bottom or last bits)"
    def pushQueueNBits(self, bits):
        self.lastBitsCache = self.lastBitsCache + bits
        while len(self.lastBitsCache) >= 8:
            idx = 8
            self.remainingBytes.append(utils.fromBinary(self.lastBitsCache[0:idx]))
            self.lastBitsCache = self.lastBitsCache[idx:]

    # returns all bytes if the data stored can be returned as bytes
    def getAllBytes(self):
        if self.firstBitsCache != "" or self.lastBitsCache != "":
            raise RuntimeError("can't getAllBytes from bitField; not all data stored in bytes now")
        else:
            return self.remainingBytes
