# ghostpass

Ghostpass is a dead simple password management system that enables users to distribute cleartext-like ciphertext to the open web, while still maintaining security and data integrity.

Don't use this yet! I'm not done. I'm just flexing my contributions.

## 1. Introduction


> The lack of use of third-party libraries and modules allow us to demonstrate the efficiencies of such a password manager using just
> native Python functionality. Of course, utilizing such other libraries / modules are still feasible, but performance and security must
> be evaluated accordingly.

### 1.1 Problems

1. Web-based password managers are centralized, and data breech for undiscovered vulnerability results in catastrophic events.
2. Modern offline clients ( i.e KeePass) don't enable for fast distribution across hosts, and portability to unencrypt anymore.

### 1.2 Features

## 2. How does it all work?

### Encryption Process

1. Client is opened (web, app, CLI).
2. User creates master password and supplies corpus file.
3. User stores key information
4. AES Encrytion using master password
5. Padding is added.
6. Corpus file is Markov-chained and resultant ciphertext appears as cleartext
8. Passwords distributed as singular text file or zipped up multiple text files

### Decryption Process

1. Client is opened
2. User supplies master password and corpus file
3. Padding is removed
3. AES ciphertext is recovered from corpus ciphertext.
4. AES Decryptio using master password
5. User views sensitive information

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
    - If no session is opened, cleartext field is mandatory for session-less encryption

ghostpass decrypt <corpus> <ciphertext>
    - Decrypts specific ciphertext with corpus and master key
    - Works independent of whether user is in session or not

ghostpass destruct <session>
    - Destroys <session>
    - If only one session exists and session argument not provided,
    that is opened as default

```

## 4. Contribution

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
