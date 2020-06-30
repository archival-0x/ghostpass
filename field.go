// Provides the high level definition for the `Field` struct, which encapsulates and performs AEAD
// on secrets in order to return for storage back into the credential store mapping.
package ghostpass

import (
	"strings"
    "encoding/hex"
	"github.com/awnumar/memguard"
)

// represents a strongly typed field, a struct that encapsulates a secret attribute that represents
// an encrypted username and password combination. Given a deniable combo pair, the secret can be
// mutated through a one-time pad and a deniable key can be derived for plausible deniability
type Field struct {
    Username string
    Password *memguard.Enclave
	Secret string
}

// given a key, service key and auth combination, create a completely new field that is encrypted
func NewField(key [32]byte, username string, pwd *memguard.Enclave) (*Field, error) {

	// unseal the password
	clearpwd, err := pwd.Open()
	if err != nil {
		return nil, err
	}

	// initialize the secret
	var secretstr strings.Builder
	secretstr.WriteString(username)
	secretstr.WriteString(":")
	secretstr.WriteString(string(clearpwd.Bytes()))

	// encrypt the secret with the key
	secret, err := BoxEncrypt(key, []byte(secretstr.String()))
	if err != nil {
		return nil, err
	}

    // hex dump the encryped sercret
    out := make([]byte, hex.EncodedLen(len(secret)))
    hex.Encode(out, secret)

	return &Field{
		Secret: string(out),
	}, nil
}

// TODO
// given a bogus and deniable auth combo, generate a secret like with the original pair and store it for
// deniable key generation later.
//func (f *Field) AddDeniableSecret(username string, pwd *memguard.Enclave) {
//    return
//}

// deconstruct the secret stored within the field, and derive back the original username and
// password combination for output consumption.
func (f *Field) DecryptFieldSecret(key [32]byte) (string, string, error) {
	plaintext, err := BoxDecrypt(key, []byte(f.Secret))
	if err != nil {
		return "", "", err
	}

	// split by substring
	creds := strings.Split(string(plaintext), ":")
	return creds[0], creds[1], nil
}

// given an encrypted service parameter and compressed field string, decrypt them all
// and reconstruct a `Field` from them.
func FromCompressed(key *memguard.Enclave, compressed string) *Field {
	var field *Field
	field.Secret = compressed
	//field.DeniableSecret = nil
	return field
}
