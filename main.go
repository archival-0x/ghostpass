package main

import (
    "os"
    "log"
    "fmt"

    "github.com/urfave/cli/v2"
    //"github.com/ex0dus-0x/ghostpass"
)

func main() {
    app := &cli.App {
        Name: "ghostpass",
        Usage: "secrets manager cryptosystem with plainsight distribution",
        Commands: []*cli.Command {
            {
                Name: "init",
                Category: "Database Initialization",
                Usage: "initializes a new secret database",
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
                Category: "Database Initialization",
                Usage: "completely nuke a password database",
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
                Category: "Database Operations",
                Usage: "add a new field to the password database",
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
                Category: "Database Operations",
                Aliases: []string{"rm"},
                Usage: "remove a field from the password database",
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
                Category: "Database Operations",
                Usage: "decrypt and view a specific field from the password database",
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
                Usage: "generates a plainsight file for distribution from current password database state",
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
