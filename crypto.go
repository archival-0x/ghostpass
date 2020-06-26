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


func GCMEncrypt(key_enclave *memguard.Enclave, plaintext string) (string, error) {

    // unseal the key and prepare the cipher
    key, err := key_enclave.Unseal()
    if err != nil {
        return "", err
    }

    // initialize GCM cipher
    block, err := aes.NewCipher(key)
    if err != nil {
        return "", err
    }

    // create nonce for HMAC
    nonce := make([]byte, 12)
    if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
        return "", err
    }

    aesgcm, err := cipher.NewGCM(block)
    if err != nil {
        return "", err
    }

    // generate ciphertext and return
    ciphertext := aesgcm.Seal(nil, nonce, plaintext, nil)
    return ciphertext
}

func InitField(service string, username string, pwdhash string, key *memguard.Enclave) (*Field, error) {

    // initialize the secret
    var secretstr strings.Builder
    secretstr.WriteString(username)
    secretstr.WriteString(":")
    secretstr.WriteString(pwdhash)

    // encrypt the secret with the key
    secret := GCMEncrypt(key, secretstr.String())

    return &Field {
        Key: key,
        Service: service,
        Secret: secret,
        DeniableSecret: nil,
    }
}

// given an encrypted service parameter and compressed field string, decrypt them all
// and reconstruct a `Field` from them.
func FromCompressed(key *memguard.Enclave, service string, compressed string) *Field {
    // TODO: decrypt service string
    // TODO: defragment compressed string and decrypt
    return nil
}

func (f *Field) AddDeniableSecret(username string, pwd *memguard.Enclave) {
    return
}

// after initializing an encrypted field and possibly adding a deniable secret, return a
// mapping that can be stored back into the credential store securely.
// TODO: deal with deniable secrets
func (f *Field) ToMapping() (string, string) {
    return (f.Service, f.Secret)
}
