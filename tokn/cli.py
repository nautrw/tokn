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

@click.group(cls=ClickAliasedGroup, invoke_without_command=True)
@click.pass_context
def cli(ctx: click.core.Context):
    if not os.path.isfile(KEYS_FILE):
        click.echo("New user detected. Starting setup.")

        new_password = click.prompt("New password", hide_input=True)
        password_confirm = click.prompt("Confirm new password", hide_input=True)

        if not new_password == password_confirm:
            raise click.ClickException("Passwords must be the same. Please try again.")

        random_salt = os.urandom(16)
        key = encryption.gen_password_key(new_password.encode(), random_salt)

        open(KEYS_FILE, "x")
        encryption.encrypt_to_file(KEYS_FILE, "[]", random_salt, key)

        click.echo(f'Successfully created new vault at path "{KEYS_FILE}".')
        
        ctx.obj = {
            "password": new_password,
            "keys": []
        }
    else:
        password = click.prompt("Enter your password", hide_input=True)

        try:
            keys = encryption.get_keys_with_password(KEYS_FILE, password.encode())
        except InvalidToken:
            raise click.ClickException("Incorrect password.")

        ctx.obj = {
            "password": password,
            "keys": keys
        }

commands = [add, remove, get, list, change_password,]
for command in commands:
    cli.add_command(command)