# ghostpass

Ghostpass is a dead simple password management protocol that enables users to distribute cleartext-like ciphertext to the open web, while still maintaining security and data integrity.

> Don't use this yet! I'm not done. I'm just flexing my contributions.

## 1. Introduction

> The lack of use of third-party libraries and modules allow us to demonstrate the efficiencies of such a password manager using just
> native Python functionality. Of course, utilizing such other libraries / modules are still feasible, but performance and security must
> be evaluated accordingly.

Ghostpass is a password management protocol that is designed with the purpose of transmitting secrets through the open web, while being able to maintain security and 

### 1.1 Problems

There's quite a bit of password managers that are out there today, so why even bother with Ghostpass? In order to answer this question, let's take a look at several different password managers "models" that already exist, and the problems that plague them:

* __Web-based password managers__ are centralized, and data breeches because of undiscovered vulnerability results in catastrophic events.
* __Offline clients__ ( i.e KeePass) don't enable for fast distribution across hosts and portability. They share a unified filetype that require KeePass-compliant client implementations in order to open.
* __Deterministic password managers__, which are able to produce memory-less and session-less cryptographically secure passwords, fail because of varying password policies and the inability to keep state. Read more [here](https://tonyarcieri.com/4-fatal-flaws-in-deterministic-password-managers).

We aim to fix these problems through a novel protocol that keep cryptographic insecurity at a minimum, enable for maximum portability, while still securely keeping state.

### 1.2 Features

TODO

### 1.3 Important Definitions

__secret__ - a key-value representation of a username and its password

__field__ - the name the identifies a specific secret

__corpus__ - a file that is parsed for Markov chain generation

## 2. How does it all work?

Ghostpass is __NOT__ a singular password manager, but rather a protocol that can be employed through various languages and technologies. For more information about the designof the cryptographic protocol and an evaluation of its security, refer to the whitepaper (TODO).

For a simplified introduction, we see the protocol as a __two-round encryption process__ that includes a key-derivation function (KDF) and a textual steganography process.


## 3. Help

```

Available Commands:

ghostpass help <command>
    - Prints help for a specific command

ghostpass init
    - Creates a new ghostpass session with master password
    - Pseudo-random ID created to identify session

ghostpass open <session>
    - Opens ghostpass session with master password
    - If only one session exists and session argument not provided,
    that is opened as default

ghostpass close
    - Closes ghostpass session, if any is opened
    - Changes should be STASHED to original session to save

ghostpass add <field>
    - Adds a new secret associated with <field> to current session

ghostpass remove <field>
    - Removes secret associated with <field> from current session

ghostpass view <field>
    - Shows unencrypted secret associated with <field> in current session

ghostpass stash
    - Commits changes made in opened session
    - Does not close session, but only writes changes to it

ghostpass list
    - Shows all sessions created by user

ghostpass secrets
    - Shows all fields and respective secrets in current session

ghostpass encrypt
    - Creates encrypted ciphertext with specified corpus of current session
    - Does not work independently

ghostpass decrypt <corpus> <ciphertext>
    - Decrypts specific ciphertext with corpus and master key
    - Works independent of whether user is in session or not

ghostpass destruct <session>
    - Destroys <session>
    - If only one session exists and session argument not provided,
    that is destructed as default

```

## 4. Example Usage

```
$ ghostpass init
$ ghostpass open <SESSION>
$ ghostpass add facebook
$ ghostpass stash
$ ghostpass close
```

## 5. Contribution

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

To setup a development environment:

```
$ pip install virutalenv
$ virtualenv env/
$ source env/bin/activate
$ pip install -r requirements.txt
```

## TODO

* Robust file validity to enforce no tampering
* Uniform pickl-ing rather than JSON de/serialiazation for session inits
