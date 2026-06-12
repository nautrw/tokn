from math import floor

import click
from cryptography.fernet import InvalidToken
from platformdirs import PlatformDirs

import tokn.encryption as encryption
import tokn.otp as otp

dirs = PlatformDirs("tokn", "nautrw", ensure_exists=True)
KEYS_FILE = dirs.user_data_dir + "/keys"

@click.argument("name", required=True)
def get(name: str):
    """Retrieve the TOTP code of the service NAME.

    NAME is the name of the service.
    """
    password = click.prompt("Enter your password", hide_input=True).encode()

    try:
        keys = encryption.get_keys_with_password(KEYS_FILE, password)
    except InvalidToken:
        raise click.ClickException("Incorrect password.")

    issuers = set([entry["issuer"] for entry in keys])

    if name not in issuers:
        raise click.ClickException(f"No issuer {name} found.")

    accounts = [key for key in keys if key["issuer"] == name]

    for account in accounts:
        click.echo(f"- {account['label']}")
        secret_key = account["secret"]

        totp = otp.generate_totp(secret_key)
        time_remaining = otp.get_time_remaining(secret_key)
        next_code = otp.get_next_totp(secret_key)

        click.echo(f"   Code: {totp}")
        click.echo(f"   {floor(time_remaining)} seconds left")
        click.echo(f"   Next code: {next_code}")
