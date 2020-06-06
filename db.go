package ghostpass

const (
    // default storage path for databases
    StoragePath string = "~/.ghostpass"
)


type Database struct {
    name string
    path string
}

func NewDatabase(name string) *Database {
    return &Database {
        name: name,
        path:
    }
}
