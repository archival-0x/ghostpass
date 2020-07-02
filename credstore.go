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
    // current protocol version
    Version int = 2.0

	// default configuration storage path for credential stores
	StoragePath string = ".ghostpass"

    // represents the state that the store is at where it's residing
    StoreStationary string = "Stationary"
    StorePlainsight string = "Plainsight"
)


// Helper routine that helps check for the existence to the credential store path, and reads its
// content for initialization and interaction.
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


// Defines a serializable `CredentialStore`, which can be instantiated to securely hold credentials
// in the form of `Field`s, and exported for plainsight distribution.
type CredentialStore struct {

    // ghostpass protocol version
    Version int `json:"version"`

    // represents the state of the store. when exported, it will swap to Plainsight
    StoreState string `json:"state"`

	// name identifier for the credential store
    Name string `json:"name"`

	// represents a hashed and secured key for symmetric encryption
    SymmetricKey []byte `json:"key"`

	// internal state of the store with all the available credentials and secrets
    Fields map[string]*Field `json:"fields"`
}


///////////////////////////////////////////////////////////////////////////////////////
//
//     DATABASE INITIALIZATION
//
///////////////////////////////////////////////////////////////////////////////////////


// Initializes a new `CredentialStore` given a name and master symmetric key that is secured. Will
// create a new store if name does not exist, otherwise will read and return the existing one.
func InitStore(name string, pwd *memguard.Enclave) (*CredentialStore, error) {

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

    // initialize as SHA hash
	checksum := sha256.Sum256(key.Bytes())

	// destroy original plaintext key
	defer key.Destroy()

	// check if there is already existing data, and deserialize, set the hashed symmetric key
	// and return the state
	if len(data) != 0 {
		var credstore CredentialStore

        // TODO: swap to custom marshal
		if err := json.Unmarshal(data, &credstore); err != nil {
			return nil, err
		}

        // TODO: check to see if checksum matches the one in store. This is only done when
        // importing stationary states of the credential store, not exporting from a plainsight
        // file, as there could be several deniable keys used.
		return &credstore, nil
	}

	// if not, create an empty CredentialStore
	return &CredentialStore{
        Version:      Version,
        StoreState:   StoreStationary,
		Name:         name,
        SymmetricKey: checksum[:],
		Fields:       make(map[string]*Field),
	}, nil
}


// Nukes the entire state of a given credential store, deleting all traces of it in-memory and
// the path to the file-based database.
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


// Commits any changes made to the current state of the existing `CredentialStore` back to the
// file-based database to ensure that operations all persist.
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


///////////////////////////////////////////////////////////////////////////////////////
//
//     DATABASE OPERATIONS
//
///////////////////////////////////////////////////////////////////////////////////////


// Add a new field to the credential store, given a service as key, and a credential pair for
// encryption and storage. Will overwrite if already exists.
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


// Given an existing field, attempt to encrypt a deniable credential pair, an derive a "deniability" key for
// plausible deniability. (TODO)
func (cs *CredentialStore) AddDeniableField(service string, username string, pwd *memguard.Enclave) error {
    // check to see if the field exists
    _, ok := cs.Fields[service]
    if !ok {
        return errors.New("cannot find entry given the service name provided")
    }

    // TODO
    // if exists, update it with the deniable secret
    //field.AddDeniableSecret(username, pwd)
    //cs.Fields[service] = field
    return nil
}


// Given a service name as the key, delete an entry corresponding to it in the credential store.
func (cs *CredentialStore) RemoveField(service string) error {
	// check to see if field exists in store
	if _, ok := cs.Fields[service]; !ok {
		return errors.New("cannot find entry given the service name provided")
	}

	// remove the field safely by service key
	delete(cs.Fields, service)
	return nil
}


// Given a service name as the key, reveal the contents safely for the given entry.
func (cs *CredentialStore) GetField(service string) (string, string, error) {
	val, ok := cs.Fields[service]
	if !ok {
		return "", "", errors.New("cannot find entry given the service name provided")
	}

    // unseal user and password
    user, err := val.Username.Open()
    if err != nil {
        return "", "", err
    }

    pwd, err := val.Pwd.Open()
    if err != nil {
        return "", "", err
    }

    // decrypt password
    pwdstr, err := BoxEncrypt(cs.SymmetricKey, pwd.Bytes())
    if err != nil {
        return "", "", err
    }

	// retrieve the username and password combo and return
    return string(user.Bytes()), string(pwdstr), nil
}


///////////////////////////////////////////////////////////////////////////////////////
//
//     PLAINSIGHT DISTRIBUTION
//
///////////////////////////////////////////////////////////////////////////////////////


// given a corpus to hide in, take the current state of the credential store,
// and export a version of it hidden within the corpus through zero-width encoding
func (cs *CredentialStore) Export(corpus string) (string, error) {
	// serialize structure into JSON
	data, err := cs.PlainsightMarshal()
	if err != nil {
		return "", err
	}

    // TODO: generate compressed data

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
