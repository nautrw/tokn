import json
import os
from hashlib import new
from math import floor

import click
import pyotp
from click_aliases import ClickAliasedGroup
from cryptography.fernet import InvalidToken

import tokn.encryption as encryption
from tokn.encryption import KEYS_FILE
import tokn.otp as otp
from tokn.commands.write_commands import add, remove, change_password
from tokn.commands.getters import get, list
from tokn.qr import read_qr_code

@click.group(cls=ClickAliasedGroup)
@click.pass_context
def cli(ctx):
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
        
        ctx.obj = {
            "password": new_password,
            "keys": []
        }
    else:
        password = click.prompt("Enter your password", hide_input=True).encode()

        try:
            keys = encryption.get_keys_with_password(KEYS_FILE, password)
        except InvalidToken:
            raise click.ClickException("Incorrect password.")

        ctx.obj = {
            "password": password,
            "keys": keys
        }

cli.add_command(add)
cli.add_command(remove)
cli.add_command(get)
cli.add_command(list)
cli.add_command(change_password)