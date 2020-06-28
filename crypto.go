// Provides the high level definition for the `Field` struct, which encapsulates and performs AEAD
// on secrets, as well as helper routines interfacing symmetric cryptographic primitives.
package ghostpass

import (
    "io"
    "strings"
    "crypto/aes"
    "crypto/rand"
    "crypto/cipher"
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


func GCMEncrypt(enclave *memguard.Enclave, plaintext []byte) (string, error) {

    // unseal the key and prepare the cipher
    key, err := enclave.Open()
    if err != nil {
        return "", err
    }

    // initialize GCM cipher
    block, err := aes.NewCipher(key.Bytes())
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
    return string(ciphertext), nil
}


func GCMDecrypt(enclave *memguard.Enclave, ciphertext []byte) (string, error) {
    // unseal the key and prepare the cipher
    key, err := enclave.Open()
    if err != nil {
        return "", err
    }

    // initialize GCM cipher
    block, err := aes.NewCipher(key.Bytes())
    if err != nil {
        return "", err
    }

    aesgcm, err := cipher.NewGCM(block)
    if err != nil {
        return "", err
    }

    // decrypt given the ciphertext
    output, err := aesgcm.Open(nil, nonce, ciphertext, nil)
    if err != nil {
        return "", err
    }

    return "", nil
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

func (f *Field) AddDeniableSecret(username string, pwd *memguard.Enclave) {
    return
}

// after initializing an encrypted field and possibly adding a deniable secret, return
// TODO: deal with deniable secrets
func (f *Field) ToCompressed() (string, string, error) {
    // encrypt the `service` field, in order to remain indistinguishable
    enc_service, err := GCMEncrypt(f.Key, []byte(f.Service))
    if err != nil {
        return "", "", err
    }
    return enc_service, f.Secret, nil
}
