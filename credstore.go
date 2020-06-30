package ghostpass

import (
	"crypto/sha256"
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"os"

	"github.com/awnumar/memguard"
)

const (
	// default configuration storage path for credential stores
	StoragePath string = ".ghostpass"
)

// defines a serializable credential store, which can be instantiated to securely
// store secrets within a field of the store
type CredentialStore struct {

	// name identifier for the credential store
	Name string

	// represents a hashed and secured key for symmetric encryption
	SymmetricKey *memguard.Enclave

	// internal state of the store with all the available credentials and secrets
	Fields map[string]*Field
}

// given a name to a credential store, check to see if it exists within the ghostpass workspace,
// and return the serialized contents given, or else `nil` if the file is newly initialized.
func InitPath(name string) ([]byte, error) {

	// data to be read from file that is open or initialized
	var data []byte

	// get absolute path to ghostpass workspace
	storepath := fmt.Sprintf("%s/%s", os.Getenv("HOME"), StoragePath)

	// check if storage path exists, if not, create
	if _, err := os.Stat(storepath); os.IsNotExist(err) {
		os.Mkdir(storepath, os.ModePerm)
	}

	// initialize path to database, open/create it, and return the contents
	dbpath := fmt.Sprintf("%s/%s.gp", storepath, name)
	if _, err := os.Stat(dbpath); os.IsNotExist(err) {

		// open file with flags to create if not found
		file, err := os.OpenFile(dbpath, os.O_RDWR|os.O_CREATE, 0755)
		if err != nil {
			return data, err
		}

		// read contents from file, regardless of what is in it
		if _, err := file.Read(data); err != nil {
			return data, err
		}
		return data, nil

	} else {
		return data, err
	}
}

// initializes a credential store given a path to the database, with appropriate
// error-handling when necessary. Database that does not exist within workspace is initialized
// as an empty credential store.
func InitCredentialStore(name string, pwd *memguard.Enclave) (*CredentialStore, error) {

	// given a name to a db, open/create it from the workspace, and read bytes for serialization
	data, err := InitPath(name)
	if err != nil {
		return nil, err
	}

	// given a secured plaintext password, unseal from secure memory, create a hash checksum from it, which
	// can be checked against when re-opening for other credential store interactions.
	key, err := pwd.Open()
	if err != nil {
		return nil, err
	}
	checksum := sha256.Sum256(key.Bytes())

	// lock up the new hash checksum copy
	symkey := memguard.NewBufferFromBytes(checksum[:])

	// destroy original plaintext key
	defer key.Destroy()

	// check if there is already existing data, and deserialize, set the hashed symmetric key
	// and return the state
	if string(data) != "" {
		var credstore CredentialStore
		if err := json.Unmarshal(data, &credstore); err != nil {
			return nil, err
		}
		credstore.SymmetricKey = symkey.Seal()
		return &credstore, nil
	}

	// if not, create an empty CredentialStore
	return &CredentialStore{
		Name:         name,
		SymmetricKey: symkey.Seal(),
		Fields:       nil,
	}, nil
}

// adds a new field to the credential store, given a service, and a username and secured buffer
// with a password.
func (cs *CredentialStore) AddField(service string, username string, pwd *memguard.Enclave) error {

	// initialize a new field from the given parameters
	field, err := NewField(cs.SymmetricKey, username, pwd)
	if err != nil {
		return err
	}

	// set encrypted mapping between service and the cred secret it represents
	cs.Fields[service] = field
	return nil
}

/*
// if configured, updates a given field with a deniable secret combination that can be decrypted if given the generated
// deniable master key.
func (cs *CredentialStore) AddDeniableField(service string, username string, pwd *memguard.Enclave) error {
    // check to see if the field exists
    field, ok := cs.Fields[service]
    if !ok {
        return errors.New("cannot find entry given the service name provided")
    }

    // if exists, update it with the deniable secret
    field.AddDeniableSecret(username, pwd)
    cs.Fields[service] = field
    return nil
}
*/

// given a service name as the key, delete the entire entry from the map that stores each credential field
func (cs *CredentialStore) RemoveField(service string) error {
	// check to see if field exists in store
	if _, ok := cs.Fields[service]; !ok {
		return errors.New("cannot find entry given the service name provided")
	}

	// remove the field safely by service key
	delete(cs.Fields, service)
	return nil
}

// given a service name as the key, reveal the contents safely for the given entry
func (cs *CredentialStore) GetField(service string) (string, string, error) {
	val, ok := cs.Fields[service]
	if !ok {
		return "", "", errors.New("cannot find entry given the service name provided")
	}

	// retrieve the username and password combo and return
	return val.DecryptFieldSecret(cs.SymmetricKey)
}

// when exporting for plainsight distribution, this makes sure that the service
// keys are indistinguishable if extracted
func (cs *CredentialStore) EncryptMarshal(compressed bool) ([]byte, error) {

	// represents finalized encrypted mapping to return
	var encfields map[string]string

	// encrypt all the service keys for indistinguishability
	for service, field := range cs.Fields {
		// encrypt the service key to check if within the mapping
		encservice, err := BoxEncrypt(cs.SymmetricKey, []byte(service))
		if err != nil {
			return nil, err
		}

		// TODO: if deniable secret is included, apply one-time pad

		// copy the fields with encrypted service key and compressed secret
		encfields[string(encservice)] = field.Secret
		delete(cs.Fields, service)
	}

	// return the finalized encrypted state
	return json.Marshal(&struct {
		Name   string            `json:"name"`
		Fields map[string]string `json:"fields"`
	}{
		Name:   cs.Name,
		Fields: encfields,
	})
}

// when importing from either an exported plainsight file or an existing persistent database,
// decrypt a JSONified string back to a `CredentialStore` given a secured symmetric key.
func DecryptUnmarshal(enclave *memguard.Enclave, serialized []byte) (*CredentialStore, error) {

	// turn the serialized JSON back into an initial state for a CredentialStore
	var csmap struct {
		Name   string            `json:"name"`
		Fields map[string]string `json:"fields"`
	}
	err := json.Unmarshal(serialized, &csmap)
	if err != nil {
		return nil, err
	}

	// initialize new credential store
	var cs CredentialStore
	cs.SymmetricKey = enclave

	// create new unencrypted fields mapping
	var fields map[string]Field

	for servicekey, secret := range csmap.Fields {

		// first, decrypt the encrypted service keys
		service, err := BoxDecrypt(enclave, []byte(servicekey))
		if err != nil {
			return nil, err
		}

		// initialize field from compressed secret
		field := FromCompressed(enclave, secret)

		// then, decompress the string representation for secrets back into a field
		fields[string(service)] = field
		delete(csmap.Fields, servicekey)
	}
	return nil, nil
}

// any changes that are written to the credential store structure are then saved to the persistent
// store in the workspace.
func (cs *CredentialStore) CommitStore() error {

	// construct and open path to credential store
	storepath := fmt.Sprintf("%s/%s", os.Getenv("HOME"), StoragePath)
	dbpath := fmt.Sprintf("%s/%s.gp", storepath, cs.Name)

	// serialize structure for writing to file
	data, err := json.Marshal(cs)
	if err != nil {
		return err
	}

	// write new state back to the store
	return ioutil.WriteFile(dbpath, data, 0644)
}

// nukes the entire state of a given credential store, deleting all traces of it in-memory and
// on the filesystem.
func (cs *CredentialStore) DestroyStore() error {

	// construct path to workspace
	storepath := fmt.Sprintf("%s/%s", os.Getenv("HOME"), StoragePath)
	dbpath := fmt.Sprintf("%s/%s.gp", storepath, cs.Name)

	// delete the persistent path
	err := os.Remove(dbpath)
	if err != nil {
		return err
	}

	// golang garbage collection so delete in-memory struct once out of scope, but force it
	cs = nil
	return nil
}

// given a corpus to hide in, take the current state of the credential store,
// and export a version of it hidden within the corpus through zero-width encoding
func (cs *CredentialStore) Export(corpus string) (string, error) {
	// serialize structure into JSON
	// TODO: compressed
	data, err := cs.EncryptMarshal(true)
	if err != nil {
		return "", err
	}

	// generate compressed data

	// generate resultant plainsight output
	res := EncodeHiddenString(corpus, data)
	return res, nil
}

func Import(key *memguard.Enclave, encoded string, persist bool) (*CredentialStore, error) {
	// extract out the db
	// decompress the compressed string
	// attempt to unmarshal into a struct
	// set symmetric master key to struct
	// decrypt service keys with master key
	// if persist is set, write changes to new or existing state
	return nil, nil
}
