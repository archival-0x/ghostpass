# ghostpass

Ghostpass is a dead simple password management system that enables users to distribute cleartext-like ciphertext to the open web, while still maintaining security and data integrity.

## Problems

1. Web-based password managers are centralized, and data breech for undiscovered vulnerability results in catastrophic events.
2. Modern clients (KeePass) don't enable for fast distribution across hosts, and portability to unencrypt anymore.

## Encryption Process

1. Client is opened (web, app, CLI).
2. User creates master password and supplies corpus file.
3. User stores key information
4. AES Encrytion using master password
5. Padding is added.
6. Corpus file is Markov-chained and resultant ciphertext appears as cleartext
8. Passwords distributed as singular text file or zipped up multiple text files

## Decryption Process

1. Client is opened
2. User supplies master password and corpus file
3. Padding is removed
3. AES ciphertext is recovered from corpus ciphertext.
4. AES Decryptio using master password
5. User views sensitive information
