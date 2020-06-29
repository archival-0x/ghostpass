package ghostpass

import (
    "io"
    "crypto/aes"
    "crypto/rand"
    "crypto/cipher"
    "github.com/awnumar/memguard"
)

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

