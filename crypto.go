package ghostpass

import (
	"errors"
	"github.com/awnumar/memguard"
	"golang.org/x/crypto/nacl/secretbox"
	"unsafe"
)

// given a sealed symmetric key and a plaintext byte array, encrypt it using
// the Nacl secretbox API, which provides authenticated encryption
func BoxEncrypt(enclave *memguard.Enclave, plaintext []byte) ([]byte, error) {

	// unseal the key and prepare the cipher
	key, err := enclave.Open()
	if err != nil {
		return nil, err
	}

	// check if length is 32 bytes
	if len(key.Bytes()) != 32 {
		return nil, errors.New("Invalid symmetric key length")
	}

	// create nonce for HMAC seeding through memguard
	var nonce [24]byte
	memguard.ScrambleBytes(nonce[:])

	// get a pointer to sized byte array for symmetric encryption
	keyptr := (*[32]byte)(unsafe.Pointer(&key.Bytes()[0]))

	// encrypt and return result
	return secretbox.Seal(nonce[:], plaintext, &nonce, keyptr), nil
}

func BoxDecrypt(enclave *memguard.Enclave, ciphertext []byte) ([]byte, error) {
	// unseal the key and prepare the cipher
	key, err := enclave.Open()
	if err != nil {
		return nil, err
	}

	// check if key length is 32 bytes
	if len(key.Bytes()) != 32 {
		return nil, errors.New("Invalid symmetric key length")
	}

	// retrieve nonce from ciphertext, which is appended at the end
	var nonce [24]byte
	copy(nonce[:], ciphertext[:24])

	// get a pointer to sized byte array for symmetric encryption
	keyptr := (*[32]byte)(unsafe.Pointer(&key.Bytes()[0]))

	// decrypt with error checking
	plaintext, ok := secretbox.Open(nil, ciphertext[24:], &nonce, keyptr)
	if !ok {
		return nil, errors.New("Decryption on ciphertext fialed")
	}
	return plaintext, nil
}
