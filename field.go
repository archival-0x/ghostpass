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
    Key *memguard.Enclave
    DeniableKey *memguard.Enclave
    Service string
    Secret string
    DeniableSecret *string
}


func InitField(key *memguard.Enclave, service string, username string, pwd *memguard.Enclave) (*Field, error) {

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
    secret, err := GCMEncrypt(key, []byte(secretstr.String()))
    if err != nil {
        return nil, err
    }

    return &Field {
        Key: key,
        DeniableKey: nil,
        Service: service,
        Secret: secret,
        DeniableSecret: nil,
    }, nil
}

// given an encrypted service parameter and compressed field string, decrypt them all
// and reconstruct a `Field` from them.
func FromCompressed(key *memguard.Enclave, service string, compressed string) *Field {
    // TODO: decrypt service string
    // TODO: defragment compressed string and decrypt
    return nil
}

// TODO: deal with deniable secret
func (f *Field) ToCompressed() string {
    return f.Secret
}

func (f *Field) AddDeniableSecret(username string, pwd *memguard.Enclave) {
    return
}
