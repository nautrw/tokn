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
## Advanced
- The keys file is stored in their best location depending on the operating system:

Linux: `/home/USER/.local/share/tokn/keys`

MacOS: `/Users/USER/Library/Application Support/tokn/keys`

Windows: `C:\Users\USER\AppData\Local\nautrw\tokn/keys`

- Commands are split among several files in `tokn/commands`, and imported back into `tokn/cli.py` to be added under the `cli` command group, allowing for commands like `tokn add`
- A `pyproject.toml` file is used for treating the project as a package, allowing the use of `pip install -e .` and uploading to PyPI in the future
- - The `cli` function in `tokn/cli.py` is what gets run; it is specified in the `[project.scripts]` section in the file

### Technologies/libraries used
- The `pyotp` library is used to generate the TOTP codes as specified in [RFC 6238](https://www.rfc-editor.org/info/rfc6238/)
- The `cryptography` library, specially `fernet`, is used to encrypt files
- [Argon2](https://argon2.online), as implemented by the `cryptography` library, is used to generate password hashes that are used as keys for `fernet`
- The `click` library to make it a CLI app
- The `zxingcpp` and `opencv` libraries for QR code scanning
