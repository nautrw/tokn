import click
import tokn.otp as otp
import pyotp
import tokn.encryption as encryption
import json
from math import floor


@click.group()
def cli():
    pass


@cli.command()
@click.argument("name", required=True)
def add(name: str):
    """Associate a secret key to the service NAME.

    NAME is the name of the service.
    """
    password = click.prompt("Enter your password", hide_input=True).encode()
    keys_dict = encryption.get_keys_with_password("keys", password)

    secret_key = click.prompt("Enter the secret key", hide_input=True)

    keys_dict[name] = secret_key

    salt, encrypted = encryption.get_file_info("keys")
    key = encryption.
    encryption.encrypt_to_file("keys", json.dumps(keys_dict), salt, key)

    click.echo(f"Successfully added key to {name}")


@cli.command()
@click.argument("name", required=True)
def get(name: str):
    """Retrieve the TOTP code of the service NAME.

    NAME is the name of the service.
    """
    password = click.prompt("Enter your password", hide_input=True).encode()
    keys_dict = encryption.get_keys_with_password("keys", password)

    secret_key = keys_dict[name]

    totp = otp.generate_totp(secret_key)
    time_remaining = otp.get_time_remaining(secret_key)
    next_code = otp.get_next_totp(secret_key)

    click.echo(f"Code: {totp}")
    click.echo(f"{floor(time_remaining)} seconds left")
    click.echo(f"Next code: {next_code}")
