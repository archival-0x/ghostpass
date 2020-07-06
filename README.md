# ghostpass

Privacy-First Secrets Management Cryptosystem

## Project Roadmap

This is still on-going and a work-in-progress.

* [x] Plainsight Distribution
* [ ] Plausible deniability
* [ ] Keybase filesystem integration

## Introduction

__Ghostpass__ is a secrets management cryptography scheme that can hide encrypted secrets in cleartext for the purpose of distribution across public mediums. It ensures that your secrets, whether in the form of authentication credentials or actual documentation, can appear in plainsight as normal cleartexts, and can be confidently transmitted even in a public medium with potential malicious actors, even those that may act out with coercion.

Ghostpass is _novel_ in the sense that it applies modern symmetric cryptography towards digital consumer privacy through the use of textual steganography and plausible deniability. However, it should also be considered _novelty_ because it is __NOT__ a full replacement for current cryptographic software, but an ongoing effort to bridge together cryptography and privacy research. I encourage users to criticize, audit and expose shortcomings in order to better understand how these types of implementations can better be harnessed in the space of digital privacy.

There's quite a bit of password/secrets managers that are out there today, so why even bother with Ghostpass? In order to answer this question, let's take a look at different password managers "models" that already exist, and the problems that plague them:

* __Web-based password managers__ are centralized, and data breaches are possible since they are central points of failure.
* __Offline clients__ ( i.e KeePass) don't enable for fast distribution across hosts and portability. They share a unified filetype that require compliant client implementations to work

Ghostpass's implementation aims to create a compromise that doesn't require the authority of a password management service, but can still enable portability for users across whatever mediums they choose.

## Features

* __Secure__ - all fields in credential stores are properly protected in-memory and on-disk, such that attackers with priviledged access to the host can't recover jack.
* __Cryptographically Secure__ - symmetric encryption occurs using the secret-key authentication encryption scheme XSalsa20-Poly1305.
* __Privacy-Centric__ - supports "plainsight distribution" using zero-width encoding to hide ciphertext within plaintext, and plausible deniability (TODO) to give back fake entries under coercion.

## Use Cases

* Hide and encrypt sensitive and private information away before going into an area of surveillance (ie. airport, government building).
* Use plainsight distribution as a means to make cold storage of keys safer on a host and in transmission.
* Employ a provably secure "digital book cipher" as a medium of transmission with another party.

### Who Can Use Ghostpass?

* __Journalists__ - hide secrets amongst corpuses of actual documents, and use plausible deniability to return bogus articles if ever interrogated
* __Lawyers__ - protect confidentiality of clients and sensitive anecdotes before trial by encrypting them amongst fake ones.
* __You, a Privacy-Conscious Digital Consumer__

## Usage

### Build

The Ghostpass command-line application and library package can be installed to your host with the following:

```
$ go get github.com/ex0dus-0x/ghostpass/
```

However, to minimize the exfiltration of information from the user from a misuser, we recommend the usage of a Docker container:

```
TODO
```

To use:

```
$ ghostpass help
```

## Contributing

To create a new branch for contributions:

```
$ git remote add upstream https://github.com/ex0dus-0x/ghostpass
$ git checkout -b my-branch-name
$ # do code, do tests, etc etc
$ git add .
$ git commit -m "Useful commit message"
$ git push origin my-branch-name
```

Of course, remember to `git fetch` for changes.

## License

[MIT License](https://codemuch.tech/license.txt)
