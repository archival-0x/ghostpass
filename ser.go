// Implements helper routines useful for de/serialization for both the stationary and plainsight states in order to
// securely JSONify credential store state for storage.
package ghostpass

import (
    "encoding/json"
)


func (cs *CredentialStore) Marshal() ([]byte, error) {


}


// Helper routine that helps prepare a credential store to be plainsight distributable, by
// incorporating indistinguishability to all entries, and stripping the symmetric key checksum,
// and applying one-time pads for deniability.
func (cs *CredentialStore) PlainsightMarshal() ([]byte, error) {

    // stores a final compressed mapping for the credential store's fields, where
    // keys are encrypted for indistinguishability and a compressed form of the credential pair
    // is also created to map against for serialization.
	var encfields map[string]string

	// encrypt all the service keys for indistinguishability
	for service, field := range cs.Fields {

		// encrypt the service key
		encservice, err := BoxEncrypt(cs.SymmetricKey, []byte(service))
		if err != nil {
			return nil, err
		}

		// TODO: if deniable secrets are found, apply one-time pad to mutate secret
        secret := field.Secret

		// store the new encrypted entry
		encfields[string(encservice)] = secret
	}

	// return the finalized plainsight-compliant state
	return json.Marshal(&struct {
        Version     int               `json:"version"`
        StoreState  string            `json:"state"`
		Name        string            `json:"name"`
		Fields      map[string]string `json:"fields"`
	}{
        Version:        Version,
        StoreState:     StorePlainsight,
		Name:           cs.Name,
		Fields:         encfields,
	})
}


// Helper routine that consumes a key and serialized JSON buffer of a credential store in plainsight mode,
// and deserializes it back into a usable CredentialStore
func PlainsightUnmarshal(enclave *memguard.Enclave, serialized []byte) (*CredentialStore, error) {

	// turn the serialized JSON back into an initial state for a CredentialStore
	var csmap struct {
        Version     int               `json:"version"`
        StoreState  string            `json:"state"`
		Name        string            `json:"name"`
		Fields      map[string]string `json:"fields"`
	}
	err := json.Unmarshal(serialized, &csmap)
	if err != nil {
		return nil, err
	}

    // given a secured plaintext password, unseal from secure memory, create a hash checksum from it, which
	// can be checked against when re-opening for other credential store interactions.
	key, err := enclave.Open()
	if err != nil {
		return nil, err
	}

    // initialize as SHA hash
	checksum := sha256.Sum256(key.Bytes())

	// destroy original plaintext key
	defer key.Destroy()

	// create new unencrypted fields mapping
	var fields map[string]*Field

	for servicekey, secret := range csmap.Fields {

		// first, decrypt the encrypted service key
        service, err := BoxDecrypt(checksum[:], []byte(servicekey))
		if err != nil {
			return nil, err
		}

		// reinitialize field from compressed secret
		field := ReconstructField(enclave, secret)

		// then, decompress the string representation for secrets back into a field
		fields[string(service)] = field
		delete(csmap.Fields, servicekey)
	}

    // return the CredentialStore as if nothing changed
	return &CredentialStore {
        Version:        csmap.Version,
        StoreState:     StoreStationary,
        Name:           csmap.Name,
        SymmetricKey:   checksum[:],
        Fields:         fields,
    }, nil
}

