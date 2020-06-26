package ghostpass

import (
    "fmt"
    "strings"
    "strconv"
)

const (
    // ZWJ represents zero-width joiner.
    ZWJ = '\u200D'

    // ZWNJ represents zero-width non-joiner.
    ZWNJ = '\u200C'
)

// TODO: construct error

// Checks to see if a given corpus file contains zero-width characters already
func ContainsHiddenChars(corpus string) bool {
	return strings.ContainsRune(corpus, ZWJ) ||
		strings.ContainsRune(corpus, ZWNJ)
}

// given a plaintext string corpus and a secret to hide, encode it with zero-width characters
func EncodeHiddenString(plain string, secret []byte) string {

    // TODO: compress the bytes representing the secret

    // convert secret string into binary representation
    var binary []byte
    for _, c := range secret {
        binary = strconv.AppendInt(binary, int64(c), 2)
    }

    // use a strings builder to push unicode characters from binary bytearray
    var corpus strings.Builder
    corpus.WriteString(plain)
    for b := range binary {
        if b == 1 {
            corpus.WriteString(string(ZWJ))
        } else if b == 0 {
            corpus.WriteString(string(ZWNJ))
        }
    }

    // return finalized string representation
    return corpus.String()
}

// given a corpus string with encoded zero-width characters, find them and strip them back
// for deserialization,
func DecodeHiddenString(corpus string) []byte {
    var binresult []byte

    // iterate through corpus and parse out zero-width unicode chars
    for b := range []byte(corpus) {
        binresult = append(binresult, b)
    }

    // decode

    return result
}
