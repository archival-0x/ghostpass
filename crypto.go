package ghostpass

import (
	"errors"
    "unsafe"
    "github.com/awnumar/memguard"
	"golang.org/x/crypto/nacl/secretbox"
)

// given a sealed symmetric key and a plaintext byte array, encrypt it using
// the Nacl secretbox API, which provides authenticated encryption
func BoxEncrypt(key []byte, plaintext []byte) ([]byte, error) {
    if len(key) != 32 {
        return nil, errors.New("")
    }

    // get an unsafe reference to pointer
    keyptr := (*[32]byte)(unsafe.Pointer(&key[0]))

	// create nonce for HMAC seeding through memguard
	var nonce [24]byte
	memguard.ScrambleBytes(nonce[:])

	// encrypt and return result
	return secretbox.Seal(nonce[:], plaintext, &nonce, keyptr), nil
}

func BoxDecrypt(key []byte, ciphertext []byte) ([]byte, error) {
    if len(key) != 32 {
        return nil, errors.New("")
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
