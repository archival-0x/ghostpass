# ghostpass

Ghostpass is a dead simple password management system that enables users to distribute cleartext-like ciphertext to the open web, while still maintaining security and data integrity.

Don't use this yet! I'm not done. I'm just flexing my contributions.

## 1. Introduction


> The lack of use of third-party libraries and modules allows us to demonstrate the efficiencies of such password managers using just
> native Python functionality. Of course, utilizing such libraries / modules is still feasible, but performance and security must
> be evaluated accordingly.

### 1.1 Problems

1. Web-based password managers are centralized and data breaches due to zero day vulnerabilities result in catastrophic events.
2. Modern offline clients (e.g KeePass) fail to allow for fast distribution across hosts and portability of decryption.

### 1.2 Features


### 1.3 Important Definitions

__secret__ - a key-value representation of a username and its password

__field__ - the name that identifies a specific secret

__corpus__ - a file that is parsed for Markov chain generation

## 2. How does it all work?

The idea of __ghostpass__ is presented as not a singular password manager, but rather a protocol that can be implemented flexibly.

### Encryption Process

1. Client is opened (web, app, CLI)
2. User creates master password and supplies corpus file
3. User stores key information
4. AES Encrytion using master password
5. Padding is incorporated
6. Corpus file is Markov-chained and resultant ciphertext appears as cleartext
8. Passwords are distributed in a single text file or zipped up in multiple text files

### Decryption Process

1. Client is opened
2. User supplies master password and corpus file
3. Padding is removed
3. AES ciphertext is recovered from corpus ciphertext
4. AES Decryption using master password
5. User accesses sensitive information

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
    - If only one session exists and session argument is not provided,
    that is opened as default

ghostpass close
    - Closes ghostpass session, if open

ghostpass add <field>
    - Adds a new secret associated with <field> to current session

ghostpass remove <field>
    - Removes secret associated with <field> from current session

ghostpass view <field>
    - Shows unencrypted secret associated with <field> in current session

ghostpass stash
    - Commits changes made in opened session

ghostpass list
    - Shows all sessions created by user

ghostpass secrets
    - Shows all fields and respective secrets in current session

ghostpass encrypt <corpus> <cleartext>
    - Creates encrypted ciphertext with specified corpus of current session
    - Works independent of whether user is in session or not
    - If no session is opened, cleartext field is mandatory for 'session-less' encryption

ghostpass decrypt <corpus> <ciphertext>
    - Decrypts specific ciphertext with corpus and master key
    - Works independent of whether user is in session or not

ghostpass destruct <session>
    - Destroys <session>
    - If only one session exists and session argument is not provided,
    that is opened as default

```

## 4. Contribution

To create a new branch for contributions:

```
$ git remote add upstream https://github.com/ex0dus-0x/ghostpass
$ git checkout -b my-branch-name
$ # write code, perform tests, etc etc
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
