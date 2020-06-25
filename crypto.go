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
    Service string
    Secret string
    DeniableSecret *string
}

func InitField(service string, username string, pwdhash string, key *memguard.Enclave) *Field {
    var secret strings.Builder
    secret.WriteString(username)
    secret.WriteString(pwdhash)

    return &Field {
        Key: key,
        Service: service,
        Secret: secret.String(),
        DeniableSecret: nil,
    }
}

// given an encrypted service parameter and compressed field string, decrypt them all
// and reconstruct a `Field` from them.
func FromCompressed(key *memguard.Enclave, service string, compressed string) *Field {
    return nil
}

func (f *Field) AddDeniableSecret(username string, pwd *memguard.Enclave) {
    return
}

func (f *Field) ToCompressed() string {
    return ""
}

