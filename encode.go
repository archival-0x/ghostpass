package ghostpass

import "strings"

const (
    // ZWJ represents zero-width joiner.
    ZWJ = '\u200D'

    // ZWNJ represents zero-width non-joiner.
    ZWNJ = '\u200C'
)


// Checks to see if a given corpus file contains zero-width characters
func ContainsHiddenChars(corpus string) bool {
	return strings.ContainsRune(corpus, ZWJ) ||
		strings.ContainsRune(corpus, ZWNJ)
}
