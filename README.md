# ghostpass

[![Actions][actions-badge]][actions-url]

[actions-badge]: https://github.com/ghostpass/ghostpass/workflows/CI/badge.svg?branch=master
[actions-url]: https://github.com/ghostpass/ghostpass/actions

Privacy-First Secrets Management Cryptosystem

> WARNING: this is experimental software and should not be used in production.

## Introduction

__Ghostpass__ is a command-line tool that helps symmetrically encrypt your secrets, and makes it feasible for plainsight distribution. It ensures that your secrets, whether in the form of authentication credentials or 
actual messages and documents, can appear in plainsight as normal cleartexts, and can be confidently transmitted even in a public medium with potential malicious actors, even those that may act out with coercion to exfiltrate and decrypt it.

Ghostpass is _novel_ in the sense that it applies modern symmetric cryptography towards digital consumer privacy to mitigate [rubber-hose cryptoanalysis](https://en.wikipedia.org/wiki/Rubber-hose_cryptanalysis). 
However, it should also be considered _novelty_ because it is __NOT__ a full replacement for current cryptographic software.

## Use Cases

* Hide and encrypt sensitive and private information away before going into an area of surveillance (ie. airport, government building).
* Use plainsight distribution as a means to make cold storage of keys safer on a host or in transmission.
* Employ a provably secure "digital book cipher" as a medium of transmission with another party.

## Usage

There is on-going support for Ghostpass across different mediums, including the web and chatops. However, Ghostpass can still be used locally through the command line.

### Command Line

The Ghostpass command line application can be installed locally as follows:

```
$ go get -u github.com/ghostpass/ghostpass/cmd/ghostpass
```

Docker is also supported if you want to minimize exfiltration on a host:

```
$ docker build .
```

To use:

```
$ ghostpass help
```

## Contributing

To create a new branch for contributions:

```
# new feature branch
$ git remote add upstream https://github.com/ghostpass/ghostpass
$ git checkout -b my-branch-name

# do code, do tests, etc
$ git add .
$ git commit -m "Useful commit message"

# push and make pull request
$ git push origin my-branch-name
```

## License

[MIT License](https://opensource.org/licenses/MIT)
