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
from tokn.commands.write_commands import add, remove
from tokn.commands.getters import get, list
from tokn.qr import read_qr_code

dirs = PlatformDirs("tokn", "nautrw", ensure_exists=True)
KEYS_FILE = dirs.user_data_dir + "/keys"


@click.group(cls=ClickAliasedGroup)
@click.pass_context
def cli(ctx):
    if not os.path.isfile(KEYS_FILE) and not ctx.invoked_subcommand == "init":
        raise click.ClickException("Keys file not initialized. Please run `tokn init`.")

@cli.command()
def init():
    """Set up a new keys file."""
    if os.path.isfile(KEYS_FILE):
        raise click.ClickException(
            f"There is already an existing keys file at ."
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


cli.add_command(add)
cli.add_command(remove)
cli.add_command(get)
cli.add_command(list)