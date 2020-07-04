// Implements helper routines useful for de/serialization for both the stationary and plainsight states in order to
// securely JSONify credential store state for storage.
package ghostpass

import (
    "encoding/json"
)

// Helper function that converts a stationary persistent store back into a `CredentialStore` for interaction.
// Putting the store in stationary mode preserves more state than plainsight mode, so not much decryption is needed.
func StationaryUnmarshal(checksum [32]byte, serialized []byte) (*CredentialStore, error) {

    // turn the serialized JSON back into a partially initialized state for a CredentialStore
	var cs struct {
        Version         int                   `json:"version"`
        StoreState      string                `json:"state"`
		Name            string                `json:"name"`
		Fields          map[string]*Field     `json:"fields"`
	}
	err := json.Unmarshal(serialized, &cs)
	if err != nil {
		return nil, err
	}

    // no need to decrypt service, since this it's not encrypted. We are also
    // not making a copy since we are just mutating the state of the fields
	for _, field := range cs.Fields {
        // rederive attributes of partial field
        if err := field.RederiveAuthPair(checksum[:]); err != nil {
            return nil, err
        }
	}

    // return the CredentialStore as if nothing changed
	return &CredentialStore {
        Version:        cs.Version,
        StoreState:     cs.StoreState,
        Name:           cs.Name,
        SymmetricKey:   checksum[:],
        Fields:         cs.Fields,
    }, nil
}


// Helper routine that prepares a credential store from an exported plainsight
// distribution. Since the state stored on disk does not contain any remnants of the auth
// credentials per field, this unmarshaller rederives that using the given symmetric key.
func PlainsightUnmarshal(checksum [32]byte, serialized []byte) (*CredentialStore, error) {

	// turn the serialized JSON back into a partially initialized state for a CredentialStore
	var cs struct {
        Version         int               `json:"version"`
        StoreState      string            `json:"state"`
		Name            string            `json:"name"`
		Fields          map[string][]byte `json:"fields"`
	}
	err := json.Unmarshal(serialized, &cs)
	if err != nil {
		return nil, err
	}


    // create new semi-unencrypted mapping
	var fields map[string]*Field

	for servicekey, secret := range cs.Fields {

        // decrypt service key if store file was plainsight exported
        service, err := BoxDecrypt(checksum[:], []byte(servicekey))
        if err != nil {
            return nil, err
        }

		// reinitialize field from compressed secret
        field, err := ReconstructField(checksum[:], secret)
        if err != nil {
            return nil, err
        }

		// decompress the string representation for secrets back into a field
		fields[string(service)] = field
		delete(cs.Fields, servicekey)
	}

    // return the CredentialStore as if nothing changed
	return &CredentialStore {
        Version:        cs.Version,
        StoreState:     StoreStationary,
        Name:           cs.Name,
        SymmetricKey:   checksum[:],
        Fields:         fields,
    }, nil
}

// Helper routine that helps prepare a credential store to be plainsight distributable, by
// incorporating indistinguishability to all entries, and stripping the symmetric key checksum,
// and applying one-time pads for deniability.
func (cs *CredentialStore) PlainsightMarshal() ([]byte, error) {

    // stores a final compressed mapping for the credential store's fields, where
    // keys are encrypted for indistinguishability and a compressed form of the credential pair
    // is also created to map against for serialization.
	var encfields map[string][]byte

	// encrypt all the service keys for indistinguishability
	for service, field := range cs.Fields {

		// encrypt the service key
		encservice, err := BoxEncrypt(cs.SymmetricKey, []byte(service))
		if err != nil {
			return nil, err
		}

		// TODO: if deniable secrets are found, apply one-time pad to mutate secret
        secret := field.AuthPair

		// store the new encrypted entry
		encfields[string(encservice)] = secret
	}

	// return the finalized plainsight-compliant state
	return json.Marshal(&struct {
        Version     int               `json:"version"`
        StoreState  string            `json:"state"`
		Name        string            `json:"name"`
		Fields      map[string][]byte `json:"fields"`
	}{
        Version:        Version,
        StoreState:     StorePlainsight,
		Name:           cs.Name,
		Fields:         encfields,
	})
}
