package main

import (
    "os"
    "log"
    "fmt"

    "github.com/urfave/cli/v2"
    "github.com/awnumar/memguard"
)

func ReadKeyFromStdin() (*memguard.Enclave, error) {
	key, err := memguard.NewBufferFromReaderUntil(os.Stdin, '\n')
	if err != nil {
		return nil, err
	}
	if key.Size() == 0 {
		return nil, errors.New("no input received")
	}
	return key.Seal(), nil
}


func main() {
    app := &cli.App {
        Name: "ghostpass",
        Usage: "secrets manager cryptosystem with plainsight distribution",
        Commands: []*cli.Command {
            {
                Name: "init",
                Category: "Initialization",
                Usage: "initializes a new secret credential store",
                Flags: []cli.Flag{
                    &cli.BoolFlag{Name: "dbname", Aliases: []string{"n"}},
                },
                Action: func(c *cli.Context) error {
                    fmt.Println("init")
                    return nil
                },
            },
            {
                Name: "destruct",
                Category: "Initialization",
                Usage: "completely nuke a credential store given its name",
                Flags: []cli.Flag{
                    &cli.BoolFlag{Name: "dbname", Aliases: []string{"n"}},
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
                    &cli.BoolFlag{Name: "dbname", Aliases: []string{"n"}},
                    &cli.BoolFlag{Name: "service", Aliases: []string{"s"}},
                    &cli.BoolFlag{Name: "username", Aliases: []string{"u"}},
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
                    &cli.BoolFlag{Name: "dbname", Aliases: []string{"n"}},
                    &cli.BoolFlag{Name: "service", Aliases: []string{"s"}},
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
                    &cli.BoolFlag{Name: "dbname", Aliases: []string{"n"}},
                    &cli.BoolFlag{Name: "service", Aliases: []string{"s"}},
                },
                Action: func(c *cli.Context) error {
                    fmt.Println("view")
                    return nil
                },
            },
            {
                Name: "import",
                Category: "Distribution",
                Usage: "imports a new password database given a plainsight file",
                Action: func(c *cli.Context) error {
                    fmt.Println("import")
                    return nil
                },
            },
            {
                Name: "export",
                Category: "Distribution",
                Usage: "generates a plainsight file for distribution from current state",
                Flags: []cli.Flag{
                    &cli.BoolFlag{Name: "dbname", Aliases: []string{"n"}},
                    &cli.BoolFlag{Name: "corpus", Aliases: []string{"s"}},
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
