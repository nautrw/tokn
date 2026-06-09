import click
import tokn.otp as otp
import pyotp
import tokn.encryption as encryption
import json
from math import floor
import os


@click.group()
@click.pass_context
def cli(ctx):
    if not os.path.isfile("keys") and not ctx.invoked_subcommand == "init":
        exit("Keys file not initialized. Please run `tokn init`.")


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

    salt = encryption.get_file_info("keys")[0]
    key = encryption.gen_password_key(password, salt)
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


@cli.command()
def init():
    """Set up a new keys file."""
    if os.path.isfile("keys"):
        exit("There is already an existing keys file.")

    passwd_input1 = click.prompt("Please create a new password", hide_input=True)
    passwd_input2 = click.prompt("Please enter the password again", hide_input=True)

    if not passwd_input1 == passwd_input2:
        exit("Passwords must be the same. Please try again.")

    random_salt = os.urandom(16)
    key = encryption.gen_password_key(passwd_input1.encode(), random_salt)

    open("keys", "x")
    encryption.encrypt_to_file("keys", "{}", random_salt, key)

    click.echo("Successfully created new keys file.")
