package main

import (
    "os"
    "log"
    "fmt"
    "errors"
    "syscall"

    "github.com/urfave/cli/v2"
    "github.com/manifoldco/promptui"
    "github.com/awnumar/memguard"
    "github.com/ex0dus-0x/ghostpass"
    "golang.org/x/crypto/ssh/terminal"
)

const (
	Description string = "Secrets manager cryptosystem with plainsight distribution"
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


func init() {
    // initialize new workspace directory if not set
    _ = ghostpass.MakeWorkspace()

    // install interrupt handler for sudden exist to purge cache
    memguard.CatchInterrupt()
    defer memguard.Purge()
}


func main() {
    fmt.Printf(`
        .__                    __
   ____ |  |__   ____  _______/  |____________    ______ ______
  / ___\|  |  \ /  _ \/  ___/\   __\____ \__  \  /  ___//  ___/
 / /_/  >   Y  (  <_> )___ \  |  | |  |_> > __ \_\___ \ \___ \
 \___  /|___|  /\____/____  > |__| |   __(____  /____  >____  >
/_____/      \/           \/       |__|       \/     \/     \/

        %s

`, Description)
    app := &cli.App {
        Name: "ghostpass",
        Usage: Description,
        Commands: []*cli.Command {
            {
                Name: "init",
                Category: "Initialization",
                Usage: "Create a new secret credential store",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "dbname", Aliases: []string{"n"}},
                },
                Action: func(c *cli.Context) error {
                    dbname := c.String("dbname")
                    if dbname == "" {
                        return errors.New("Name to credential store not specified")
                    }
                    fmt.Printf("Initializing new credential store `%s`\n\n", dbname)

                    // read master key and store in buffer safely
                    fmt.Printf("> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    fmt.Printf("\n\n")
                    if err != nil {
                        return err
                    }

                    // create new credential store
                    store, err := ghostpass.InitStore(dbname, masterkey)
                    if err != nil {
                        return err
                    }

                    // commit, writing the empty store to its new path
                    if err := store.CommitStore(); err != nil {
                        return err
                    }

                    fmt.Println("Successfully initialized new credential store", dbname)
                    return nil
                },
            },
            {
                Name: "destruct",
                Category: "Initialization",
                Usage: "completely nuke a credential store given its name",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "dbname", Aliases: []string{"n"}},
                },
                Action: func(c *cli.Context) error {
                    dbname := c.String("dbname")
                    if dbname == "" {
                        return errors.New("Name to credential store not specified.")
                    }

                    // read master key for the credential store
                    fmt.Printf("\n> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    fmt.Println()
                    if err != nil {
                        return err
                    }

                    // open the credential store for deletion
                    store, err := ghostpass.OpenStore(dbname, masterkey)
                    if err != nil {
                        return err
                    }

                    // ask for user confirmation
					prompt := promptui.Select{
						Label: `Are you SURE you want to do this? The credential store will be
                    	permanently deleted on this host.`,
						Items: []string{"Yes", "No"},
					}
					_, result, err := prompt.Run()
					if err != nil {
                        return err
					}

                    if result != "Yes" {
                        fmt.Println("\n\nExiting...")
                        return nil
                    }

                    // nuke!
                    store.DestroyStore()
                    fmt.Println("\n\nSuccessfully nuked the credential store! Poof!")
                    return nil
                },
            },
            {
                Name: "add",
                Category: "Operations",
                Usage: "add a new field to the credential store",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "dbname", Aliases: []string{"n"}},
                    &cli.StringFlag{Name: "service", Aliases: []string{"s"}},
                    &cli.StringFlag{Name: "username", Aliases: []string{"u"}},
                },
                Action: func(c *cli.Context) error {
                    dbname := c.String("dbname")
                    if dbname == "" {
                        return errors.New("Name to credential store not specified.")
                    }

                    service := c.String("service")
                    if service == "" {
                        return errors.New("Name of service to add not specified.")
                    }

                    username := c.String("username")
                    if username == "" {
                        return errors.New("Username for service to add not specified.")
                    }

                    // read master key for the credential store
                    fmt.Printf("\n\t> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    fmt.Println()
                    if err != nil {
                        return err
                    }

                    // open the credential store for adding the new field
                    store, err := ghostpass.OpenStore(dbname, masterkey)
                    if err != nil {
                        return err
                    }

                    // read password for service and store in buffer safely
                    fmt.Printf("\t> Password for `%s` (will not be echoed): ", service)
                    pwd, err := ReadKeyFromStdin()
                    fmt.Printf("\n\n")
                    if err != nil {
                        return err
                    }

                    // check if key already exists and warn user of overwrite
                    if store.FieldExists(service) {
					    prompt := promptui.Select{
                            Label: "Field already exists in credential store. Overwrite?",
                            Items: []string{"Yes", "No"},
					    }
                        _, result, err := prompt.Run()
                        if err != nil {
                            return err
                        }

                        if result != "Yes" {
                            fmt.Println("\n\nExiting...")
                            return nil
                        }
                    }

                    // add the new field to the store and error-handle
                    if err := store.AddField(service, username, pwd); err != nil {
                        return err
                    }

                    // commit, writing the changes to the persistent store
                    if err := store.CommitStore(); err != nil {
                        return err
                    }

                    fmt.Println("\n[*] Successfully added field to credential store [*]")
                    return nil
                },
            },
            {
                Name: "remove",
                Category: "Operations",
                Aliases: []string{"rm"},
                Usage: "remove a field from the credential store",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "dbname", Aliases: []string{"n"}},
                    &cli.StringFlag{Name: "service", Aliases: []string{"s"}},
                },
                Action: func(c *cli.Context) error {
                    dbname := c.String("dbname")
                    if dbname == "" {
                        return errors.New("Name to credential store not specified.")
                    }

                    service := c.String("service")
                    if service == "" {
                        return errors.New("Name of service to add not specified.")
                    }

                    // read master key for the credential store
                    fmt.Printf("\n\t> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    fmt.Println()
                    if err != nil {
                        return err
                    }

                    fmt.Println()

                    // open the credential store for removing the field
                    store, err := ghostpass.OpenStore(dbname, masterkey)
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
                Category: "Operations",
                Usage: "decrypt and view a specific field from the credential store",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "dbname", Aliases: []string{"n"}},
                    &cli.StringFlag{Name: "service", Aliases: []string{"s"}},
                },
                Action: func(c *cli.Context) error {
                    dbname := c.String("dbname")
                    if dbname == "" {
                        return errors.New("Name to credential store not specified.")
                    }

                    service := c.String("service")
                    if service == "" {
                        return errors.New("Name of service to add not specified.")
                    }

                    // read master key for the credential store
                    fmt.Printf("\n\t> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    fmt.Println()
                    if err != nil {
                        return err
                    }

                    // open the credential store for adding the new field
                    store, err := ghostpass.OpenStore(dbname, masterkey)
                    if err != nil {
                        return err
                    }

                    // derive the combo entry from field given the service key
                    user, pwd, err := store.GetField(service)
                    if err != nil {
                        return err
                    }

                    // TODO: ascii table
                    fmt.Printf("\n| %s : %s |\n", user, pwd)
                    return nil
                },
            },
            {
                Name: "import",
                Category: "Distribution",
                Usage: "imports a new password database given a plainsight file",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "corpus", Aliases: []string{"s"}},
                },
                Action: func(c *cli.Context) error {
                    corpus := c.String("corpus")
                    if corpus == "" {
                        return errors.New("No corpus provided for plainsight decoding.")
                    }

                    // read master key for the credential store
                    fmt.Printf("\t> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    fmt.Println()
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
                Category: "Distribution",
                Usage: "generates a plainsight file for distribution from current state",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "dbname", Aliases: []string{"n"}},
                    &cli.StringFlag{Name: "corpus", Aliases: []string{"s"}},
                },
                Action: func(c *cli.Context) error {
                    dbname := c.String("dbname")
                    if dbname == "" {
                        return errors.New("Name to credential store not specified.")
                    }

                    corpus := c.String("corpus")
                    if corpus == "" {
                        return errors.New("No corpus provided for plainsight encoding.")
                    }

                    // TODO: optional file name to export it as

                    // read master key for the credential store
                    fmt.Printf("\t> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    if err != nil {
                        return err
                    }

                    // open the credential store for adding the new field
                    store, err := ghostpass.OpenStore(dbname, masterkey)
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
