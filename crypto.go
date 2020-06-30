package ghostpass

import (
	"errors"
    "github.com/awnumar/memguard"
	"golang.org/x/crypto/nacl/secretbox"
)

// given a sealed symmetric key and a plaintext byte array, encrypt it using
// the Nacl secretbox API, which provides authenticated encryption
func BoxEncrypt(key [32]byte, plaintext []byte) ([]byte, error) {
	// create nonce for HMAC seeding through memguard
	var nonce [24]byte
	memguard.ScrambleBytes(nonce[:])

	// encrypt and return result
	return secretbox.Seal(nonce[:], plaintext, &nonce, &key), nil
}

func BoxDecrypt(key [32]byte, ciphertext []byte) ([]byte, error) {
	// retrieve nonce from ciphertext, which is appended at the end
	var nonce [24]byte
	copy(nonce[:], ciphertext[:24])

	// decrypt with error checking
	plaintext, ok := secretbox.Open(nil, ciphertext[24:], &nonce, &key)
	if !ok {
		return nil, errors.New("Decryption on ciphertext fialed")
	}
	return plaintext, nil
}
