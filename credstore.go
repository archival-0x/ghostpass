package ghostpass

import (
    "os"
    "fmt"
    "errors"
    "io/ioutil"
    "encoding/json"
    "crypto/sha256"

    "github.com/awnumar/memguard"
)

const (
    // default configuration storage path for credential stores
    StoragePath string = ".ghostpass"
)


// defines a serializable credential store, which can be instantiated to securely
// store secrets within a field of the store
type CredentialStore struct {
    Name string `json:"name"`
    SymmetricKey *memguard.Enclave `json:"-"`
    Fields map[string]string `json:"fields"`
}

// given a name to a credential store DB, check to see if it exists within the ghostpass workspace,
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
    dbpath := fmt.Sprintf("%s/%s.gp", storepath, name);
    if _, err := os.Stat(dbpath); os.IsNotExist(err) {

        // open file with flags to create if not found
        file, err := os.OpenFile(dbpath, os.O_RDWR | os.O_CREATE, 0755)
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

    // TODO: destroy key


    // if not, create an empty CredentialStore
    return &CredentialStore {
        Name: name,
        SymmetricKey: symkey.Seal(),
        Fields: nil,
    }, nil
}


// adds a new field to the credential store, given a service, and a username and secured buffer
// with a password.
func (cs *CredentialStore) AddField(service string, username string, pwd *memguard.Enclave) error {

    // initialize a new field from the given parameters
    field, err := InitField(cs.SymmetricKey, service, username, pwd)
    if err != nil {
        return err
    }

    // TODO: add in deniable key if also specified

    // add to mapping
    service, secret, err := field.ToCompressed()
    if err != nil {
        return err
    }

    // set encrypted mapping between service and the cred secret it represents
    cs.Fields[service] = secret
    return nil
}


// given a service name as the key, delete the entry from the map that stores each credential field
func (cs *CredentialStore) RemoveField(service string) {
    delete(cs.Fields, service)
}


// given a service name as the key, reveal the contents safely for the given entry
func (cs *CredentialStore) GetField(service string) error {
    val, ok := cs.Fields[service]
    if !ok {
        return errors.New("Cannot find entry given the service provided")
    }

    // decrypt the contents of the field and return for display
    field := FromCompressed(cs.SymmetricKey, service, val)

    // TODO
    return nil
}


// any changes that are written to the credential store structure are then saved to the persistent
// store in the workspace.
func (cs *CredentialStore) CommitStore() error {

    // construct and open path to credential store
    storepath := fmt.Sprintf("%s/%s", os.Getenv("HOME"), StoragePath)
    dbpath := fmt.Sprintf("%s/%s.gp", storepath, cs.Name);

    // serialize structure for writing to file
    data, err := json.Marshal(cs)
    if err != nil {
        return err
    }

    // write to file
    return ioutil.WriteFile(dbpath, data, 0644)
}


// nukes the entire state of a given credential store, deleting all traces of it in-memory and
// on the filesystem.
func (cs *CredentialStore) DestroyStore() error {

    // construct path to workspace
    storepath := fmt.Sprintf("%s/%s", os.Getenv("HOME"), StoragePath)
    dbpath := fmt.Sprintf("%s/%s.gp", storepath, cs.Name);

    // delete the persistent path
    err := os.Remove(dbpath)
    if err != nil {
        return err
    }

    // golang garbage collection so delete in-memory struct once out of scope, but force it
    // now anyways
    cs = nil
    return nil
}


// given a corpus to hide in, take the current state of the credential store,
// and export a version of it hidden within the corpus through zero-width encoding
func (cs *CredentialStore) Export(corpus string) (string, error) {
    // serialize structure into JSON
    data, err := json.Marshal(cs)
    if err != nil {
        return "", err
    }

    // compression algorithm
    // TODO
    compressed_data := data

    // generate resultant plainsight output
    res := EncodeHiddenString(corpus, compressed_data)
    return res, nil
}


func (cs *CredentialStore) Import(key *memguard.Enclave, encoded string) error {
    // extract out the
    return nil
}
