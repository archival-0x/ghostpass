# ghostpass

Ghostpass is a dead simple password management system that enables users to distribute cleartext-like ciphertext to the open web, while still maintaining security and data integrity.

## 1. Problems

1. Web-based password managers are centralized, and data breech for undiscovered vulnerability results in catastrophic events.
2. Modern clients (KeePass) don't enable for fast distribution across hosts, and portability to unencrypt anymore.

## 2. Core Functionality

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

ghostpass add <field>
    - Adds a new secret associated with <field> to current session

ghostpass remove <field>
    - Removes secret associated with <field> from current session

ghostpass view <field>
    - Shows unencrypted secret associated with <field> in current session

ghostpass list <session>
    - Shows all entries and associated IDs in current session
    - If only one session exists and session argument not provided,
    that is opened as default

ghostpass encrypt <corpus>
    - Creates encrypted ciphertext with specified corpus of current session
    - Works independent of whether user is in session or not

ghostpass decrypt <corpus> <ciphertext>
    - Decrypts specific ciphertext with corpus and master key
    - Works independent of whether user is in session or not

ghostpass destruct <session>
    - Destroys <session>
    - If only one session exists and session argument not provided,
    that is opened as default

```
