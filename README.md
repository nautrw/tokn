# tokn
Tokn is a CLI-based TOTP (time-based one-time password) code generator that uses encryption to store secret keys.
## Quick Start/Installation
### From GitHub
1. Clone the GitHub repository or download the code (using the green button)
2. Inside the directory, run the following command (you may need to add `python -m ` or `python3 -m ` before it):
```sh
pip install -e .
```
## Features
- Argon2 encryption of secret keys
- No secret keys or passwords are exposed to log files and such
- Adding keys via QR code images
## Technologies/libraries used
- The `pyotp` library is used to generate the TOTP codes as specified in [RFC 6238](https://www.rfc-editor.org/info/rfc6238/)
- The `cryptography` library, specially `fernet`, is used to encrypt files
- [Argon2](https://argon2.online), as implemented by the `cryptography` library, is used to generate password hashes that are used as keys for `fernet`
- The `click` library to make it a CLI app
- The `zxingcpp` and `opencv` libraries for QR code scanning
