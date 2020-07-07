package main

import (
    "os"
    "log"
    "fmt"
    "bufio"
    "strings"
    "errors"
    "syscall"
    "io/ioutil"
    "path/filepath"

    "github.com/urfave/cli/v2"
    "github.com/fatih/color"
    "github.com/manifoldco/promptui"
    "github.com/awnumar/memguard"
    "golang.org/x/crypto/ssh/terminal"
    "github.com/olekukonko/tablewriter"
    "github.com/ex0dus-0x/ghostpass"
)

const (
	Description string = "Privacy-First Secrets Management Cryptosystem"
)


// Helper for displaying banner. TODO: quiet down if set
func Banner() {
    color.Blue(`
        .__                    __
   ____ |  |__   ____  _______/  |____________    ______ ______
  / ___\|  |  \ /  _ \/  ___/\   __\____ \__  \  /  ___//  ___/
 / /_/  >   Y  (  <_> )___ \  |  | |  |_> > __ \_\___ \ \___ \
 \___  /|___|  /\____/____  > |__| |   __(____  /____  >____  >
/_____/      \/           \/       |__|       \/     \/     \/

`)
    col := color.New(color.FgWhite).Add(color.Underline)
    col.Printf("\t>> Version: 2.0\n\t>> https://ghostpass.codemuch.tech/\n\t>> %s\n\n", Description)
}


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
    Banner()
    app := &cli.App {
        Name: "ghostpass",
        Usage: Description,
        Commands: []*cli.Command {
            {
                Name: "init",
                Category: "Initialization",
                Usage: "Create a new secret secret store",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "dbname", Aliases: []string{"n"}},
                },
                Action: func(c *cli.Context) error {
                    dbname := c.String("dbname")
                    if dbname == "" {
                        return errors.New("Name to secret store not specified")
                    }

                    col := color.New(color.FgWhite).Add(color.Bold)
                    col.Printf("\n[*] Initializing new secret store `%s` [*]\n\n", dbname)

                    // read master key and store in buffer safely
                    fmt.Printf("> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    fmt.Printf("\n\n")
                    if err != nil {
                        return err
                    }

                    // create new secret store
                    store, err := ghostpass.InitStore(dbname, masterkey)
                    if err != nil {
                        return err
                    }

                    // commit, writing the empty store to its new path
                    if err := store.CommitStore(); err != nil {
                        return err
                    }

                    col = color.New(color.FgGreen).Add(color.Bold)
                    col.Println("[*] Successfully initialized new secret store. [*]")
                    return nil
                },
            },
            {
                Name: "stores",
                Category: "Initialization",
                Usage: "List existing secret secret stores",
                Action: func(c *cli.Context) error {
                    col := color.New(color.FgWhite).Add(color.Bold)
                    col.Println("\n[*] Listing all available secret stores [*]\n")

                    files, err := ioutil.ReadDir(ghostpass.MakeWorkspace())
                    if err != nil {
                        return err
                    }

                    for _, f := range files {
                        dbname := strings.TrimSuffix(f.Name(), filepath.Ext(f.Name()))
                        col := color.New(color.Underline).Add(color.Bold)
                        fmt.Printf("\t* ")
                        col.Println(dbname)
                    }
                    fmt.Println()
                    return nil
                },
            },
            {
                Name: "destruct",
                Category: "Initialization",
                Usage: "Completely nuke a secret store given its name",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "dbname", Aliases: []string{"n"}},
                },
                Action: func(c *cli.Context) error {
                    dbname := c.String("dbname")
                    if dbname == "" {
                        return errors.New("Name to secret store not specified.")
                    }

                    col := color.New(color.FgWhite).Add(color.Bold)
                    col.Printf("\n[*] Destroying secret store `%s` [*]\n\n", dbname)

                    // read master key for the secret store
                    fmt.Printf("> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    fmt.Println()
                    if err != nil {
                        return err
                    }

                    // open the secret store for deletion
                    store, err := ghostpass.OpenStore(dbname, masterkey)
                    if err != nil {
                        return err
                    }

                    fmt.Println()

                    // ask for user confirmation
					prompt := promptui.Select{
						Label: "Are you SURE you want to do this? You will NOT be able to go back",
						Items: []string{"Yes", "No"},
					}
					_, result, err := prompt.Run()
					if err != nil {
                        return err
					}

                    fmt.Println()

                    if result != "Yes" {
                        fmt.Println("Exiting...")
                        return nil
                    }

                    // nuke!
                    store.DestroyStore()
                    col = color.New(color.FgGreen).Add(color.Bold)
                    col.Println("[*] Successfully nuked the secret store! Poof! [*]")
                    return nil
                },
            },
            {
                Name: "add",
                Category: "Operations",
                Usage: "Add a new field to the secret store, will overwrite if exists",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "dbname", Aliases: []string{"n"}},
                    &cli.StringFlag{Name: "service", Aliases: []string{"s"}},
                    &cli.StringFlag{Name: "username", Aliases: []string{"u"}},
                },
                Action: func(c *cli.Context) error {
                    dbname := c.String("dbname")
                    if dbname == "" {
                        return errors.New("Name to secret store not specified.")
                    }

                    col := color.New(color.FgWhite).Add(color.Bold)
                    col.Printf("\n[*] Adding field entry to secret store `%s` [*]\n", dbname)

                    // read master key for the secret store
                    fmt.Printf("\n> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    fmt.Println()
                    if err != nil {
                        return err
                    }

                    // open the secret store for adding the new field
                    store, err := ghostpass.OpenStore(dbname, masterkey)
                    if err != nil {
                        return err
                    }

                    // get service if not specified in args
                    service := c.String("service")
                    if service == "" {
                        reader := bufio.NewReader(os.Stdin)
                        fmt.Print("> Service: ")
                        text, err := reader.ReadString('\n')
                        if err != nil {
                            return err
                        }
                        service = strings.TrimSuffix(text, "\n")
                    }

                    // get username if not specified in args
                    username := c.String("username")
                    if username == "" {
                        reader := bufio.NewReader(os.Stdin)
                        fmt.Print("> Username: ")
                        text, err := reader.ReadString('\n')
                        if err != nil {
                            return err
                        }
                        username = strings.TrimSuffix(text, "\n")
                    }

                    // read password for service and store in buffer safely
                    fmt.Printf("> Password for `%s` (will not be echoed): ", service)
                    pwd, err := ReadKeyFromStdin()
                    if err != nil {
                        return err
                    }

                    fmt.Printf("\n\n")

                    // check if key already exists and warn user of overwrite
                    if store.FieldExists(service) {
					    prompt := promptui.Select{
                            Label: "Field already exists in secret store. Overwrite?",
                            Items: []string{"Yes", "No"},
					    }
                        _, result, err := prompt.Run()
                        if err != nil {
                            return err
                        }

                        if result != "Yes" {
                            fmt.Println("Exiting...")
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

                    col = color.New(color.FgGreen).Add(color.Bold)
                    col.Println("[*] Successfully nuked the secret store! Poof! [*]")
                    return nil
                },
            },
            {
                Name: "remove",
                Category: "Operations",
                Aliases: []string{"rm"},
                Usage: "Remove a field from the secret store",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "dbname", Aliases: []string{"n"}},
                    &cli.StringFlag{Name: "service", Aliases: []string{"s"}},
                },
                Action: func(c *cli.Context) error {
                    dbname := c.String("dbname")
                    if dbname == "" {
                        return errors.New("Name to secret store not specified.")
                    }

                    col := color.New(color.FgWhite).Add(color.Bold)
                    col.Printf("\n[*] Removing field entry from secret store `%s` [*]\n", dbname)

                    // read master key for the secret store
                    fmt.Printf("\n> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    fmt.Println()
                    if err != nil {
                        return err
                    }

                    // open the secret store for removing the field
                    store, err := ghostpass.OpenStore(dbname, masterkey)
                    if err != nil {
                        return err
                    }

                    // get service if not specified in args
                    service := c.String("service")
                    if service == "" {
                        reader := bufio.NewReader(os.Stdin)
                        fmt.Print("> Service: ")
                        text, err := reader.ReadString('\n')
                        if err != nil {
                            return err
                        }
                        service = strings.TrimSuffix(text, "\n")
                    }

                    fmt.Println()

                    // add the new field to the store and error-handle
                    if err := store.RemoveField(service); err != nil {
                        return err
                    }

                    // commit, writing the changes to the persistent store
                    if err := store.CommitStore(); err != nil {
                        return err
                    }

                    col = color.New(color.FgGreen).Add(color.Bold)
                    col.Println("[*] Successfully nuked the secret store! Poof! [*]")
                    return nil
                },
            },
            {
                Name: "view",
                Category: "Operations",
                Usage: "Decrypt and view a specific field from the secret store",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "dbname", Aliases: []string{"n"}},
                    &cli.StringFlag{Name: "service", Aliases: []string{"s"}},
                },
                Action: func(c *cli.Context) error {
                    dbname := c.String("dbname")
                    if dbname == "" {
                        return errors.New("Name to secret store not specified.")
                    }

                    col := color.New(color.FgWhite).Add(color.Bold)
                    col.Printf("\n[*] Retrieving field entry from secret store `%s` [*]\n", dbname)

                    // read master key for the secret store
                    fmt.Printf("\n> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    fmt.Println()
                    if err != nil {
                        return err
                    }

                    // open the secret store for adding the new field
                    store, err := ghostpass.OpenStore(dbname, masterkey)
                    if err != nil {
                        return err
                    }

                    // get service if not specified in args
                    service := c.String("service")
                    if service == "" {
                        reader := bufio.NewReader(os.Stdin)
                        fmt.Print("> Service: ")
                        text, err := reader.ReadString('\n')
                        if err != nil {
                            return err
                        }
                        service = strings.TrimSuffix(text, "\n")
                    }
                    fmt.Println()

                    // derive the combo entry from field given the service key
                    combo, err := store.GetField(service)
                    if err != nil {
                        return err
                    }

                    // output ascii table
                    table := tablewriter.NewWriter(os.Stdout)
                    table.SetHeader([]string{"Service", "Username", "Password"})
                    table.SetAutoMergeCells(true)
                    table.SetRowLine(true)
                    table.Append(combo)
                    table.Render()
                    return nil
                },
            },
            {
                Name: "fields",
                Category: "Operations",
                Usage: "List all available fields in a secret store",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "dbname", Aliases: []string{"n"}},
                },
                Action: func(c *cli.Context) error {
                    dbname := c.String("dbname")
                    if dbname == "" {
                        return errors.New("Name to secret store not specified.")
                    }

                    col := color.New(color.FgWhite).Add(color.Bold)
                    col.Printf("\n[*] Retrieving all fields from secret store `%s` [*]\n", dbname)

                    // read master key for the secret store
                    fmt.Printf("\n> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    fmt.Println()
                    if err != nil {
                        return err
                    }

                    // open the secret store for adding the new field
                    store, err := ghostpass.OpenStore(dbname, masterkey)
                    if err != nil {
                        return err
                    }

                    table := tablewriter.NewWriter(os.Stdout)
                    table.SetHeader([]string{"Service"})
                    table.Append(store.GetFields())
                    table.Render()
                    return nil
                },
            },
            {
                Name: "import",
                Category: "Distribution",
                Usage: "Imports a new password database given a plainsight file",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "corpus", Aliases: []string{"c"}},
                },
                Action: func(c *cli.Context) error {
                    corpus := c.String("corpus")
                    if corpus == "" {
                        return errors.New("No path to corpus provided for plainsight decoding.")
                    }

                    // read master key for the secret store
                    fmt.Printf("\t> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    fmt.Println()
                    if err != nil {
                        return err
                    }

                    // read data out of corpus file
                    corpusdata, err := ioutil.ReadFile(corpus)
                    if err != nil {
                        return err
                    }

                    // recreate secret store given plainsight corpus
                    store, err := ghostpass.Import(masterkey, string(corpusdata), false)
                    if err != nil {
                        return err
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
                Usage: "Generates a plainsight file for distribution from current state",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "dbname", Aliases: []string{"n"}},
                    &cli.StringFlag{Name: "corpus", Aliases: []string{"c"}},
                },
                Action: func(c *cli.Context) error {
                    dbname := c.String("dbname")
                    if dbname == "" {
                        return errors.New("Name to secret store not specified.")
                    }

                    corpus := c.String("corpus")
                    if corpus == "" {
                        return errors.New("No corpus provided for plainsight encoding.")
                    }

                    // TODO: optional file name to export it as

                    // read master key for the secret store
                    fmt.Printf("\t> Master Key (will not be echoed): ")
                    masterkey, err := ReadKeyFromStdin()
                    if err != nil {
                        return err
                    }

                    // open the secret store for adding the new field
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
