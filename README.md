# tokn
Tokn is a CLI-based TOTP (time-based one-time password) code generator that uses a password-protected vault file to store secret keys.
[![asciicast](https://asciinema.org/a/GkWW4UOBH3z1jX7P.svg)](https://asciinema.org/a/GkWW4UOBH3z1jX7P)
## Installation
(Recommended)If you have [pipx](https://pipx.pypa.io/stable/) installed:
```sh
pipx install tokn-nautrw
```
Otherwise:
```sh
pip install tokn-nautrw
```
## Try it
To do a quick test without a real account:
- Download (or screenshot!) the QR code and copy the path:
<br>![qr code test](https://github.com/nautrw/tokn/blob/main/assets/qrcode.png?raw=true)

- Run `tokn add` and follow the steps
  - When asked for a path, paste the copied path
  - Accept the default values (press `y` and hit enter)
- Run `tokn get Issuer`
- The code displayed on [this website](https://totp.danhersam.com/) should be the same as one of the codes from the command
## Features
- An encrypted vault file used to store keys
- Secret keys and passwords are never exposed
- Accounts can be added via QR code screenshots, raw codes, or URIs
- CLI is designed to be as ergonomic as possible
## How It Works
Getting TOTP codes is quite tedious. Having to reach for a phone every time one wants to log in to an account they want to project can get annoying. Having a TOTP app on the CLI ideally makes this easier by not having to interact with a GUI, and on the same device but password-protected.

A brief description of TOTP:
- The app's server associates a secret key with the user's account
- The user gets the secret key, often in the form of a QR code, and stores it in an authenticator app like this one
- Both the server and the authenticator app use an algorithm that takes time as a variable (detailed in [RFC 6238](https://www.rfc-editor.org/info/rfc6238/)) to get a code
- The user inputs the code to the app when they want to log in, and the server authorizes it if its code and the user's code is the same

The Python **cryptography** library, specifically the *Fernet* module, allows for encrypting a file to store the secret keys. **Argon2** can be used to hash a password, and the hash can be used as the key to encrypt and decrypt text in Fernet.

The vault file stores the secret keys and the random salt required by Argon2. It is stored in their best location depending on the operating system:
- Linux: `/home/USER/.local/share/tokn/keys`
- MacOS: `/Users/USER/Library/Application Support/tokn/keys`
- Windows: `C:\Users\USER\AppData\Local\nautrw\tokn/keys`

Commands are split among several files in `src/tokn/commands`, and imported into `src/tokn/cli.py` to be added under the `cli` function/command group, allowing for many subcommands like `tokn add`. The `cli` function in `src/tokn/cli.py` is what gets run; it is specified in the `[project.scripts]` section in the file

### Technologies/libraries used
- The `pyotp` library is used to generate the TOTP codes as specified in [RFC 6238](https://www.rfc-editor.org/info/rfc6238/)
- The `cryptography` library, specially the `fernet` module, is used to encrypt files
  - [Argon2](https://argon2.online), as implemented by the `cryptography` library, is used to generate password hashes that are used as keys for `fernet`
- The `click` library to make it a CLI app
- The `zxingcpp` and `opencv` libraries for QR code scanning
