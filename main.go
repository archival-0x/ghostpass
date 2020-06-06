package main

import (
    "os"
    "log"
    "github.com/urfave/cli/v2"
)

func main() {
    app := &cli.App {
        Name: "ghostpass",
        Usage: "secrets manager cryptosystem with plainsight distribution",
        Commands: []*cli.Command {
            {
                Name: "init",
                Category: "Database Initialization",
                Aliases: []string{"i"},
                Usage: "initializes a new secret database",
                Action: func(c *cli.Context) error {
                    fmt.Println("init")
                    return nil
                },
            },
            {
                Name: "destruct",
                Category: "Database Initialization",
                Aliases: []string{"d"},
                Usage: "completely nuke a password database",
                Action: func(c *cli.Context) error {
                    fmt.Println("destruct")
                    return nil
                },
            },
            {
                Name: "add",
                Category: "Database Operations",
                Aliases: []string{"a"},
                Usage: "add a new field to the password database",
                Action: func(c *cli.Context) error {
                    fmt.Println("add")
                    return nil
                },
            },
            {
                Name: "remove",
                Category: "Database Operations",
                Aliases: []string{"r", "rm"},
                Usage: "remove a field from the password database",
                Action: func(c *cli.Context) error {
                    fmt.Println("rm")
                    return nil
                },
            },
            {
                Name: "view",
                Category: "Database Operations",
                Aliases: []string{"v"},
                Usage: "decrypt and view a specific field from the password database",
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
                Aliases: []string{"g"},
                Usage: "generates a plainsight file for distribution from current password database state",
                Action: func(c *cli.Context) error {
                    fmt.Println("export")
                    return nil
                },
            }
        },
    }

    err := app.Run(os.Args)
    if err != nil {
        log.Fatal(err)
    }
}
