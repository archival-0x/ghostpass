// Provides the high level definition for the `Field` struct, which encapsulates and performs AEAD
// on secrets, as well as helper routines interfacing symmetric cryptographic primitives.
package ghostpass

import (
    "strings"
    "github.com/awnumar/memguard"
)

// represents a field, a struct that derives a hash of the finalized ciphertext from a
// compressed version of the auth parameters. Note that rather than serializing the `Field`
// when marshaling, the `ToString()` routine is used instead to faciliate generation of the
// final encrypted mapping
type Field struct {
    Secret string
//    DeniableSecret *string
}


// given a key, service key and auth combination, create an encrypted field with an empty deniable secret parameter
func InitField(key *memguard.Enclave, username string, pwd *memguard.Enclave) (*Field, error) {

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

    return &Field {
        Secret: string(secret),
//        DeniableSecret: nil,
    }, nil
}


// TODO
// given a bogus and deniable auth combo, generate a secret like with the original pair and store it for
// deniable key generation later.
//func (f *Field) AddDeniableSecret(username string, pwd *memguard.Enclave) {
//    return
//}


// deconstruct the secret key stored internally and return a username and password pair
func DecryptFieldSecret(key *memguard.Enclave, secret string) (string, *memguard.Enclave, error) {
    return "", nil, nil
}


// given an encrypted service parameter and compressed field string, decrypt them all
// and reconstruct a `Field` from them.
func FromCompressed(key *memguard.Enclave, compressed string) Field {
    var field Field
    field.Secret = compressed
    //field.DeniableSecret = nil
    return field
}
