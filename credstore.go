package ghostpass

import (
    "os"
    "fmt"
    "io/ioutil"
    "encoding/json"
    "crypto/sha256"

    "github.com/awnumar/memguard"
)

const (
    // default storage path for databases
    StoragePath string = ".ghostpass"
)

type Field struct {
    Key []byte
    Secret string
    DeniableSecret *string
}

func InitField(username string, pwd *memguard.Enclave) *Field {
    var secret_key string
    return &Field {
        Secret: secret_key,
        DeniableSecret: nil,
    }
}

func (f *Field) AddDeniableSecret(username string, pwd *memguard.Enclave) {
    return
}

// defines a serializable credential store, which can be instantiated to securely
// store secrets within a field of the store
type CredentialStore struct {
    Name string `json:"name"`
    Checksum string `json:"checksum"`
    Fields map[string]Field `json:"fields"`
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
    dbpath := fmt.Sprintf("%s/%s.gp", StoragePath, name);
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
// as an empty credential store
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

    // check if there is already existing data, and deserialize and return if so
    // TODO: better way to do this?
    if string(data) != "" {
        var credstore CredentialStore
        if err := json.Unmarshal(data, &credstore); err != nil {
            return nil, err
        }
        return &credstore, nil
    }

    // if not, create an empty CredentialStore
    return &CredentialStore {
        Name: name,
        Checksum: string(checksum[:]),
        Fields: nil,
    }, nil
}

// adds a new field to the credential store, given a service, and a username and secured buffer
// with a password.
func (cs *CredentialStore) AddField(service string, username string, pwd *memguard.Enclave) error {
    return nil
}

// given a service name as the key, delete the entry from the map that stores each credential field
func (cs *CredentialStore) RemoveField(service string) {
    delete(cs.Fields, service)
}

func (cs *CredentialStore) CommitStore() error {
    // open database path
    storepath := fmt.Sprintf("%s/%s", os.Getenv("HOME"), StoragePath)
    dbpath := fmt.Sprintf("%s/%s.gp", storepath, cs.Name);

    // serialize for writing to file
    data, err := json.Marshal(cs)
    if err != nil {
        return err
    }

    // write to file
    return ioutil.WriteFile(dbpath, data, 0644)
}
