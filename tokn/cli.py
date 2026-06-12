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
from tokn.commands.write_commands import add, remove, change_password
from tokn.commands.getters import get, list
from tokn.qr import read_qr_code

dirs = PlatformDirs("tokn", "nautrw", ensure_exists=True)
KEYS_FILE = dirs.user_data_dir + "/keys"


@click.group(cls=ClickAliasedGroup)
def cli():
    if not os.path.isfile(KEYS_FILE):
        click.echo("New user detected. Starting setup.")

        new_password = click.prompt("Create a new password", hide_input=True)
        password_confirm = click.prompt("Confirm your password", hide_input=True)

        if not new_password == password_confirm:
            raise click.ClickException("Passwords must be the same. Please try again.")

        random_salt = os.urandom(16)
        key = encryption.gen_password_key(new_password.encode(), random_salt)

        open(KEYS_FILE, "x")
        encryption.encrypt_to_file(KEYS_FILE, "[]", random_salt, key)

        click.echo(f"Successfully created new keys file at {KEYS_FILE}.")

cli.add_command(add)
cli.add_command(remove)
cli.add_command(get)
cli.add_command(list)
cli.add_command(change_password)