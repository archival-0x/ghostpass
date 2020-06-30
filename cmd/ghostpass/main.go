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
                    fmt.Printf("Initializing new credential store `%s`\n\n", dbname)

                    // read master key and store in buffer safely
                    fmt.Printf("\t> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    if err != nil {
                        return err
                    }

                    // TODO: check if already exists

                    // create new credential store
                    store, err := ghostpass.InitStore(dbname, masterkey)
                    if err != nil {
                        return err
                    }

                    // commit, writing the empty store to its new path
                    if err := store.CommitStore(); err != nil {
                        return err
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
                    dbname := c.String("dbname")
                    service := c.String("service")
                    username := c.String("username")

                    // read master key for the credential store
                    fmt.Printf("\n\t> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    if err != nil {
                        return err
                    }

                    // read password for service and store in buffer safely
                    fmt.Printf("\n\t> Password for `%s` (will not be echoed): ", service)
                    pwd, err := ReadKeyFromStdin()
                    if err != nil {
                        return err
                    }

                    // open the credential store for adding the new field
                    store, err := ghostpass.InitStore(dbname, masterkey)
                    if err != nil {
                        return err
                    }

                    // TODO: check if key already exists and warn user of overwrite

                    // add the new field to the store and error-handle
                    if err := store.AddField(service, username, pwd); err != nil {
                        return err
                    }

                    // commit, writing the changes to the persistent store
                    if err := store.CommitStore(); err != nil {
                        return err
                    }

                    fmt.Println("\n\n[*] Successfully added field to credential store [*]")
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
                    dbname := c.String("dbname")
                    service := c.String("service")

                    // read master key for the credential store
                    fmt.Printf("\n\t> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    if err != nil {
                        return err
                    }

                    // open the credential store for removing the field
                    store, err := ghostpass.InitStore(dbname, masterkey)
                    if err != nil {
                        return err
                    }

                    // add the new field to the store and error-handle
                    if err := store.RemoveField(service); err != nil {
                        return err
                    }

                    // commit, writing the changes to the persistent store
                    if err := store.CommitStore(); err != nil {
                        return err
                    }

                    fmt.Println("\n\n[*] Successfully removed field from credential store [*]")
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
                    dbname := c.String("dbname")
                    service := c.String("service")

                    // read master key for the credential store
                    fmt.Printf("\t> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    if err != nil {
                        return err
                    }

                    // open the credential store for adding the new field
                    store, err := ghostpass.InitStore(dbname, masterkey)
                    if err != nil {
                        return err
                    }

                    // derive the combo entry from field given the service key
                    user, pwd, err := store.GetField(service)
                    if err != nil {
                        return err
                    }

                    fmt.Println("{} {}", user, pwd)
                    return nil
                },
            },
            {
                Name: "import",
                Category: "Database Distribution",
                Usage: "imports a new password database given a plainsight file",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "corpus", Aliases: []string{"s"}},
                },
                Action: func(c *cli.Context) error {
                    corpus := c.String("corpus")

                    // read master key for the credential store
                    fmt.Printf("\t> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    if err != nil {
                        return err
                    }

                    // TODO: read corpus file

                    // recreate credential store given plainsight corpus
                    store, err := ghostpass.Import(masterkey, corpus, false)
                    if err != nil {
                        return nil
                    }

                    // commit, writing the changes to the persistent store
                    if err := store.CommitStore(); err != nil {
                        return err
                    }
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
                    dbname := c.String("dbname")
                    corpus := c.String("corpus")

                    // TODO: optional file name to export it as

                    // read master key for the credential store
                    fmt.Printf("\t> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    if err != nil {
                        return err
                    }

                    // open the credential store for adding the new field
                    store, err := ghostpass.InitStore(dbname, masterkey)
                    if err != nil {
                        return err
                    }

                    // TODO: read corpus file

                    // given the current state the store represents, export it as a plainsight file
                    final, err := store.Export(corpus)
                    if err != nil {
                        return err
                    }
                    fmt.Println("{}", final)
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
