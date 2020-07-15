package ghostpass

import (
    "fmt"
	"strconv"
    "bytes"
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


// Helper function described here: https://stackoverflow.com/a/37350639
func StringToBin(s string) string {
    var buffer bytes.Buffer
    for _, val := range s {
        fmt.Fprintf(&buffer, "%b", val)
    }
    return fmt.Sprintf("%s", buffer.Bytes())
}


func BinToString(binstring string) (cleartext string) {
    for _, c := range binstring {
        cleartext = fmt.Sprintf("%s%s", cleartext, c)
    }
    return
}


// Given a plaintext string corpus and a secret to hide, encode it with zero-width characters by converting serialized input
// into bitstring, which is then encoded to the plaintext to hide in.
func EncodeHiddenString(plain string, secret string) string {

	// convert secret string into binary representation
	binary := StringToBin(secret)
    fmt.Println(binary)

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
// for deserialization,
func DecodeHiddenString(corpus string) []byte {

	// iterate through corpus and parse out zero-width unicode chars
	var binresult []byte

    split := 0
	for _, b := range corpus {
        if b == ZWJ {
		    binresult = append(binresult, byte('1'))
        } else if b == ZWNJ {
		    binresult = append(binresult, byte('0'))
        }

        // add split between text in order to make conversion back easier
        if split == 8 {
            binresult = append(binresult, byte(' '))
            split = 0
        }
        split += 1
	}

	// decode the bitstring back into something deserializable
	var result []byte
    for _, s := range strings.Fields(string(binresult)) {
        fmt.Printf("%s ", s)
        n, _ := strconv.ParseUint(s, 2, 8)
        result = append(result, byte(n))
    }

    fmt.Println(string(result))
	return result
}
