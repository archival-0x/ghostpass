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


// Helper routine to construct path to a ghostpass workspace for storage
// if not found in filesystem, and returns name
func MakeWorkspace() string {
    // get absolute path to ghostpass workspace
	storepath := fmt.Sprintf("%s/%s", os.Getenv("HOME"), StoragePath)

	// check if storage path exists, if not, create
	if _, err := os.Stat(storepath); os.IsNotExist(err) {
		os.Mkdir(storepath, os.ModePerm)
	}
    return storepath
}


// Helper routine to check if a given path exists.
func PathExists(path string) bool {
    if _, err := os.Stat(path); os.IsNotExist(err) {
        return false
    }
    return true
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
    SymmetricKey []byte `json:"-"`

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

    // initialize path to database, return empty buffer
	dbpath := fmt.Sprintf("%s/%s.gp", MakeWorkspace(), name)
    if PathExists(dbpath) {
        return nil, errors.New("Credential store already exists")
    }

	// create empty file
	file, err := os.Create(dbpath)
	if err != nil {
        return nil, err
	}
    file.Close()

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

	// if not, create an empty CredentialStore
	return &CredentialStore{
        Version:      Version,
        StoreState:   StoreStationary,
		Name:         name,
        SymmetricKey: checksum[:],
		Fields:       make(map[string]*Field),
	}, nil
}


// Opens an existing `CredentialStore` for interaction by the user. Will error if does not
// exist or cannot properly read and deserialize the contents of the persistent database.
func OpenStore(name string, pwd *memguard.Enclave) (*CredentialStore, error) {

    // check if store doesn't exist
	dbpath := fmt.Sprintf("%s/%s.gp", MakeWorkspace(), name)
    if !PathExists(dbpath) {
        return nil, errors.New("Credential store does not exist. Create before opening.")
    }

    // given a name to a db, create it from the workspace, and read bytes for serialization
    // open file for reading
    data, err := ioutil.ReadFile(dbpath)
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

    // use custom marshal to rederive fields
    credstore, err := StationaryUnmarshal(checksum, data)
    if err != nil {
        return nil, err
    }
	return credstore, nil
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


// Helper routine used to check if a field with a specific service already exists.
func (cs *CredentialStore) FieldExists(service string) bool {
    if _, ok := cs.Fields[service]; !ok {
        return false
    }
    return true
}


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
    if !cs.FieldExists(service) {
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
    if !cs.FieldExists(service) {
		return errors.New("cannot find entry given the service name provided")
	}

	// remove the field safely by service key
	delete(cs.Fields, service)
	return nil
}


// Given a service name as the key, reveal the contents safely for the given entry.
func (cs *CredentialStore) GetField(service string) ([]string, error) {
    if !cs.FieldExists(service) {
		return nil, errors.New("cannot find entry given the service name provided")
	}

    val := cs.Fields[service]

    // unseal user and password
    user, err := val.Username.Open()
    if err != nil {
        return nil, err
    }

    pwd, err := val.Pwd.Open()
    if err != nil {
        return nil, err
    }

    /*
    // decrypt password
    pwdstr, err := BoxDecrypt(cs.SymmetricKey, pwd.Bytes())
    if err != nil {
        return nil, err
    }
    */
    pwdstr := pwd.Bytes()

    // concatenate slice with parameters for output
    var combo []string
    combo = append(combo, service)
    combo = append(combo, string(user.Bytes()))
    combo = append(combo, string(pwdstr))
    return combo, nil
}


// Return a slice of all available services in the credential store.
func (cs *CredentialStore) GetFields() []string {
    var fields []string
    for service, _ := range cs.Fields {
        fields = append(fields, service)
    }
    return fields
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

// Given an imported compressed corpus, extract and decrypt it with a symmetric key, and attempt to reinitialize
// the state it represented when marshalled.
func Import(key *memguard.Enclave, encoded string, persist bool) (*CredentialStore, error) {
	// extract out the db
	// decompress the compressed string
	// attempt to unmarshal into a struct
	// set symmetric master key to struct
	// decrypt service keys with master key
	// if persist is set, write changes to new or existing state
	return nil, nil
}
