// Implements the functionality for performing zero-width encoding and decoding given a corpus
// and information to hide within.
package ghostpass

import (
	"bytes"
	"fmt"
	"strconv"
	"strings"
)

const (
	// ZWJ represents zero-width joiner.
	ZWJ = '\u200D'

	// ZWNJ representds zero-width non-joiner.
	ZWNJ = '\u200C'
)

// Checks to see if a given corpus file contains zero-width characters already
func ContainsHiddenChars(corpus string) bool {
	return strings.ContainsRune(corpus, ZWJ) ||
		strings.ContainsRune(corpus, ZWNJ)
}

// Helper function for converting a string of ASCII characters into a binary string.
func DataToBin(s string) string {
	var buffer bytes.Buffer
	for _, val := range s {
		fmt.Fprintf(&buffer, "%08b", val)
	}
	return buffer.String()
}

// Helper function used to convert a binary string back into a byte array of data.
func BinToData(binstring string) []byte {
	var out []byte
	for i := 0; i+8 <= len(binstring); i += 8 {
		b, err := strconv.ParseUint(binstring[i:i+8], 2, 8)
		if err != nil {
			panic(err)
		}
		out = append(out, byte(b))
	}
	return out
}

// Given a plaintext string corpus and a secret to hide, encode it with zero-width characters by converting serialized input
// into bitstring, which is then encoded to the plaintext to hide in.
func EncodeHiddenString(plain string, secret string) string {

	// convert secret string into binary representation
	binary := DataToBin(secret)

	// use a strings builder to push unicode characters from binary bytearray
	var corpus strings.Builder
	corpus.WriteString(plain)
	for _, b := range binary {
		if b == 49 { // 1
			corpus.WriteString(string(ZWJ))
		} else if b == 48 { // 0
			corpus.WriteString(string(ZWNJ))
		}
	}

	// return finalized string representation
	return corpus.String()
}

// given a corpus string with encoded zero-width characters, find them and strip them back
// into a compressed form.
func DecodeHiddenString(corpus string) []byte {

	// iterate through corpus and parse out zero-width unicode chars
	var binresult []byte
	for _, b := range corpus {
		if b == ZWJ {
			binresult = append(binresult, byte('1'))
		} else if b == ZWNJ {
			binresult = append(binresult, byte('0'))
		}
	}

	// decode the bitstring back into a compressed form.
	res := BinToData(string(binresult))
	return res
}
