package main

import (
    "os"
    "log"
    "fmt"
    "errors"
    "syscall"

    "github.com/urfave/cli/v2"
    "github.com/awnumar/memguard"
    "github.com/ex0dus-0x/ghostpass"
    "golang.org/x/crypto/ssh/terminal"
)

// Helper function to safely consume an input from STDIN and store it within a memguard-ed buffer
func ReadKeyFromStdin() (*memguard.Enclave, error) {

    // read a password from stdin
    pwd, err := terminal.ReadPassword(int(syscall.Stdin))
    if err != nil {
        return nil, err
    }

    // initialize locked buffer from cleartext
	key := memguard.NewBufferFromBytes(pwd)
	if key.Size() == 0 {
		return nil, errors.New("no input received")
	}

	return key.Seal(), nil
}

// Database Initialization routine: install interrupt handler for sudden exits and purge cache when
// execution terminates in some way.
func init() {
    memguard.CatchInterrupt()
    defer memguard.Purge()
}


func main() {
    app := &cli.App {
        Name: "ghostpass",
        Usage: "secrets manager cryptosystem with plainsight distribution",
        Commands: []*cli.Command {
            {
                Name: "init",
                Category: "Database Initialization",
                Usage: "initializes a new secret credential store",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "dbname", Aliases: []string{"n"}},
                },
                Action: func(c *cli.Context) error {

                    dbname := c.String("dbname")
                    fmt.Printf("Initializing new credential store %s\n\n", dbname)

                    // read key and store in buffer safely
                    fmt.Printf("\t> Master Key (will not be echoed): ")
                    pwd, err := ReadKeyFromStdin()
                    if err != nil {
                        fmt.Errorf("Error reading key from STDIN: %s", err)
                    }

                    // create new credential store
                    store, err := ghostpass.InitCredentialStore(dbname, pwd)
                    if err != nil {
                        fmt.Errorf("Cannot initialize new credential store: %s", err)
                    }

                    // commit, writing the empty store to its new path
                    if err := store.CommitStore(); err != nil {
                        fmt.Errorf("Cannot commit store to persistent path: %s", err)
                    }
                    return nil
                },
            },
            {
                Name: "destruct",
                Category: "Database Initialization",
                Usage: "completely nuke a credential store given its name",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "dbname", Aliases: []string{"n"}},
                },
                Action: func(c *cli.Context) error {
                    fmt.Println("destruct")
                    return nil
                },
            },
            {
                Name: "add",
                Category: "Credential Store Operations",
                Usage: "add a new field to the credential store",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "dbname", Aliases: []string{"n"}},
                    &cli.StringFlag{Name: "service", Aliases: []string{"s"}},
                    &cli.StringFlag{Name: "username", Aliases: []string{"u"}},
                },
                Action: func(c *cli.Context) error {
                    fmt.Println("add")
                    return nil
                },
            },
            {
                Name: "remove",
                Category: "Credential Store Operations",
                Aliases: []string{"rm"},
                Usage: "remove a field from the credential store",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "dbname", Aliases: []string{"n"}},
                    &cli.StringFlag{Name: "service", Aliases: []string{"s"}},
                },
                Action: func(c *cli.Context) error {
                    fmt.Println("rm")
                    return nil
                },
            },
            {
                Name: "view",
                Category: "Credential Store Operations",
                Usage: "decrypt and view a specific field from the credential store",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "dbname", Aliases: []string{"n"}},
                    &cli.StringFlag{Name: "service", Aliases: []string{"s"}},
                },
                Action: func(c *cli.Context) error {
                    fmt.Println("view")
                    return nil
                },
            },
            {
                Name: "import",
                Category: "Database Distribution",
                Usage: "imports a new password database given a plainsight file",
                Action: func(c *cli.Context) error {
                    fmt.Println("import")
                    return nil
                },
            },
            {
                Name: "export",
                Category: "Database Distribution",
                Usage: "generates a plainsight file for distribution from current state",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "dbname", Aliases: []string{"n"}},
                    &cli.StringFlag{Name: "corpus", Aliases: []string{"s"}},
                },
                Action: func(c *cli.Context) error {
                    fmt.Println("export")
                    return nil
                },
            },
        },
    }

    err := app.Run(os.Args)
    if err != nil {
        log.Fatal(err)
    }
}
