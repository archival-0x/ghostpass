package ghostpass

import (
	"errors"
	"github.com/awnumar/memguard"
	"golang.org/x/crypto/nacl/secretbox"
	"unsafe"
)

// Use symmetric authenticated encryption to generate a ciphertext given
// any plaintext byte buffer.
func BoxEncrypt(key []byte, plaintext []byte) ([]byte, error) {
	if len(key) != 32 {
		return nil, errors.New("Length of key is not 32 bytes")
	}

	// get an unsafe reference to pointer
	keyptr := (*[32]byte)(unsafe.Pointer(&key[0]))

	// create nonce for HMAC seeding through memguard
	var nonce [24]byte
	memguard.ScrambleBytes(nonce[:])

	// encrypt and return result
	return secretbox.Seal(nonce[:], plaintext, &nonce, keyptr), nil
}

// Use symmetric authenticated encryption to decrypt a plaintext from a ciphertext
// given a ciphertext byte buffer.
func BoxDecrypt(key []byte, ciphertext []byte) ([]byte, error) {
	if len(key) != 32 {
		return nil, errors.New("Length of key is not 32 bytes")
	}

	// retrieve nonce from ciphertext, which is appended at the end
	var nonce [24]byte
	copy(nonce[:], ciphertext[:24])

	// get an unsafe reference to pointer
	keyptr := (*[32]byte)(unsafe.Pointer(&key[0]))

	// decrypt with error checking
	plaintext, ok := secretbox.Open(nil, ciphertext[24:], &nonce, keyptr)
	if !ok {
		return nil, errors.New("Decryption on ciphertext failed")
	}
	return plaintext, nil
}
