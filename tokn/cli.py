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
from tokn.commands.getters import get, list, vault
from tokn.qr import read_qr_code


@click.group(cls=ClickAliasedGroup)
@click.pass_context
def cli(ctx: click.core.Context):
    pass


commands = [
    add,
    remove,
    get,
    list,
    change_password,
    vault,
]
for command in commands:
    cli.add_command(command)
