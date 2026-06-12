import json
import os
from hashlib import new
from math import floor

import click
import pyotp
from click_aliases import ClickAliasedGroup
from cryptography.fernet import InvalidToken
from platformdirs import PlatformDirs

import tokn.encryption as encryption
import tokn.otp as otp
from tokn.commands.add import add
from tokn.qr import read_qr_code

dirs = PlatformDirs("tokn", "nautrw", ensure_exists=True)
KEYS_FILE = dirs.user_data_dir + "/keys"


@click.group(cls=ClickAliasedGroup)
@click.pass_context
def cli(ctx):
    if not os.path.isfile(KEYS_FILE) and not ctx.invoked_subcommand == "init":
        raise click.ClickException("Keys file not initialized. Please run `tokn init`.")

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


@cli.command()
def init():
    """Set up a new keys file."""
    if os.path.isfile(KEYS_FILE):
        raise click.ClickException(
            f"There is already an existing keys file at {KEYS_FILE}."
        )

    new_password = click.prompt("Create a new password", hide_input=True)
    password_confirm = click.prompt("Confirm your password", hide_input=True)

    if not new_password == password_confirm:
        raise click.ClickException("Passwords must be the same. Please try again.")

    random_salt = os.urandom(16)
    key = encryption.gen_password_key(new_password.encode(), random_salt)

    open(KEYS_FILE, "x")
    encryption.encrypt_to_file(KEYS_FILE, "[]", random_salt, key)

    click.echo(f"Successfully created new keys file at {KEYS_FILE}.")


@cli.command()
def change_password():
    """Change the password of the encrypted file."""
    current_password = click.prompt("Current password", hide_input=True).encode()

    file = encryption.get_keys_with_password(KEYS_FILE, current_password)

    new_password = click.prompt("Create a new password", hide_input=True)
    new_password_confirm = click.prompt("Confirm your password", hide_input=True)

    if new_password == new_password_confirm:
        new_salt = os.urandom(16)
        new_key = encryption.gen_password_key(new_password.encode(), new_salt)

        encryption.encrypt_to_file(KEYS_FILE, json.dumps(file), new_salt, new_key)

        click.echo("Successfully changed password.")
    else:
        raise click.ClickException("Passwords must be the same. Please try again.")


@cli.command()
def list():
    """List all the services in the keys file."""
    password = click.prompt("Enter your password", hide_input=True).encode()

    try:
        keys = encryption.get_keys_with_password(KEYS_FILE, password)
    except InvalidToken:
        raise click.ClickException("Incorrect password.")

    if not keys:
        click.echo("No keys found in keys file.")
    else:
        # no, defaultdict will not work and I don't know why
        entries = {}

        for key in keys:
            if key["issuer"] not in entries.keys():
                entries[key["issuer"]] = []

            entries[key["issuer"]].append(key["label"])

        for entry in entries:
            click.echo(entry)

            for label in entries[entry]:
                click.echo(f" - {label}")


@cli.command(aliases=["rm"])
@click.argument("name", required=True)
def remove(name):
    """Remove a service NAME from the keys file."""
    password = click.prompt("Enter your password", hide_input=True).encode()

    try:
        keys = encryption.get_keys_with_password(KEYS_FILE, password)
    except InvalidToken:
        raise click.ClickException("Incorrect password.")

    if name not in keys:
        raise click.ClickException("That service is not in your keys file.")

    del keys[name]

    click.confirm(
        "Are you sure you want to delete this key? This action can not be reversed.",
        abort=True,
    )

    salt = encryption.get_file_info(KEYS_FILE)[0]
    key = encryption.gen_password_key(password, salt)
    encryption.encrypt_to_file(KEYS_FILE, json.dumps(keys), salt, key)

    click.echo(f"Successfully removed {name} from your keys.")

cli.add_command(add)