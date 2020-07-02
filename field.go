// Provides the high level definition for the `Field` struct, which encapsulates and performs AEAD
// on secrets in order to return for storage back into the credential store mapping.
package ghostpass

import (
	"strings"
    "encoding/hex"
	"github.com/awnumar/memguard"
)

// Represents a strongly typed field, a struct that encapsulates a secret attribute that represents
// an encrypted username and password combination. Given a deniable combo pair, the secret can be
// mutated through a one-time pad and a deniable key can be derived for plausible deniability
type Field struct {

    // auth credentials are securely stored for fast retrieval in memory when deserialize, but
    // will never show up in persistent storage for security.
    Username    *memguard.Enclave      `json:"-"`
    Pwd         *memguard.Enclave      `json:"-"`

    // encrypted secret of auth combo is persistently stored, and used to recover the pair
    // once deserialized back to memory securely.
    Secret      string                 `json:"secret"`
}


// Given a key, service key and auth combination, create a completely new field that is encrypted.
func NewField(key []byte, username string, pwd *memguard.Enclave) (*Field, error) {

	// unseal the password
	clearpwd, err := pwd.Open()
	if err != nil {
		return nil, err
	}

    // symmetrically encrypt pwd once first. This ensures that it
    // does not remain plaintext even when memory-guarded, and that the user
    // can redecrypt given a master key
    pwdstr, err := BoxEncrypt(key, clearpwd.Bytes())
    if err != nil {
        return nil, err
    }

    // initialize the secret by concating: `username:pwdstr`
	var secretstr strings.Builder
	secretstr.WriteString(username)
	secretstr.WriteString(":")
	secretstr.WriteString(string(pwdstr))

	// encrypt the secret with the key
	secret, err := BoxEncrypt(key, []byte(secretstr.String()))
	if err != nil {
		return nil, err
	}

    // hex dump the encryped sercret
    out := make([]byte, hex.EncodedLen(len(secret)))
    hex.Encode(out, secret)

    // memguard pwdstr and username
    user_enclave := memguard.NewBufferFromBytes([]byte(username))
    pwd_enclave := memguard.NewBufferFromBytes(pwdstr)

	return &Field{
        Username:   user_enclave.Seal(),
        Pwd:        pwd_enclave.Seal(),
		Secret:     string(secret),
	}, nil
}


// Given a bogus and deniable auth combo, generate a secret like with the original pair and store it for
// deniable key generation later. (TODO)
func (f *Field) AddDeniableSecret(username string, pwd *memguard.Enclave) {
    return
}


// Given a compressed secret, reconstruct a `Field` by decrypting it with a symmetric key, and re-deriving
// the username and password securely from them
func ReconstructField(key []byte, compressed string) (*Field, error) {

    // decrypt the secret field in order to recover username and pwd
    plaintext, err := BoxDecrypt(key, []byte(compressed))
	if err != nil {
		return nil, err
	}

	// split by by colon and return substrings
	creds := strings.Split(string(plaintext), ":")
    user, pwd := creds[0], creds[1]

    // memguard username and encrypted password
    user_enclave := memguard.NewBufferFromBytes([]byte(user))
    pwd_enclave := memguard.NewBufferFromBytes([]byte(pwd))

    // we now return the reconstructed field with the cleartext username, encrypted password,
    // and a secret checksum representing their resultant encryption.
	return &Field {
        Username: user_enclave.Seal(),
        Pwd: pwd_enclave.Seal(),
        Secret: compressed,
    }, nil
}
