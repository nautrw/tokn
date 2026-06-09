import click
from click_aliases import ClickAliasedGroup
from cryptography.fernet import InvalidToken
import tokn.otp as otp
import pyotp
import tokn.encryption as encryption
import json
from math import floor
import os

KEYS_FILE = "keys"


@click.group(cls=ClickAliasedGroup)
@click.pass_context
def cli(ctx):
    if not os.path.isfile(KEYS_FILE) and not ctx.invoked_subcommand == "init":
        exit("Keys file not initialized. Please run `tokn init`.")


@cli.command()
@click.argument("name", required=True)
def add(name: str):
    """Associate a secret key to the service NAME.

    NAME is the name of the service.
    """
    password = click.prompt("Enter your password", hide_input=True).encode()

    try:
        keys_dict = encryption.get_keys_with_password(KEYS_FILE, password)
    except InvalidToken:
        exit("Incorrect password.")

    secret_key = click.prompt("Secret key", hide_input=True)

    if name in keys_dict:
        click.confirm("That service is already added. Override?", abort=True)

    keys_dict[name] = secret_key

    salt = encryption.get_file_info(KEYS_FILE)[0]
    key = encryption.gen_password_key(password, salt)
    encryption.encrypt_to_file(KEYS_FILE, json.dumps(keys_dict), salt, key)

    click.echo(f"Successfully added key to {name}")


@cli.command()
@click.argument("name", required=True)
def get(name: str):
    """Retrieve the TOTP code of the service NAME.

    NAME is the name of the service.
    """
    password = click.prompt("Enter your password", hide_input=True).encode()

    try:
        keys_dict = encryption.get_keys_with_password(KEYS_FILE, password)
    except InvalidToken:
        exit("Incorrect password.")

    if name not in keys_dict:
        exit("Invalid service name.")

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
    if os.path.isfile(KEYS_FILE):
        exit("There is already an existing keys file.")

    passwd_input1 = click.prompt("Create a new password", hide_input=True)
    passwd_input2 = click.prompt("Confirm your password", hide_input=True)

    if not passwd_input1 == passwd_input2:
        exit("Passwords must be the same. Please try again.")

    random_salt = os.urandom(16)
    key = encryption.gen_password_key(passwd_input1.encode(), random_salt)

    open(KEYS_FILE, "x")
    encryption.encrypt_to_file(KEYS_FILE, "{}", random_salt, key)

    click.echo("Successfully created new keys file.")


@cli.command(aliases=["passwd"])
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
        exit("Passwords must be the same. Please try again.")


@cli.command()
def list():
    """List all the services in the keys file."""
    password = click.prompt("Enter your password", hide_input=True).encode()

    try:
        keys = encryption.get_keys_with_password(KEYS_FILE, password)
    except InvalidToken:
        exit("Incorrect password.")

    click.echo("Available services:")
    for service in keys.keys():
        click.echo(service)


@cli.command(aliases=["rm"])
@click.argument("name", required=True)
def remove(name):
    """Remove a service NAME from the keys file."""
    password = click.prompt("Enter your password", hide_input=True).encode()

    try:
        keys = encryption.get_keys_with_password(KEYS_FILE, password)
    except InvalidToken:
        exit("Incorrect password.")

    if name not in keys:
        exit("That service is not in your keys file.")

    del keys[name]

    confirm_delete = click.confirm(
        "Are you sure you want to delete this key? This action can not be reversed.",
        abort=True,
    )

    salt = encryption.get_file_info(KEYS_FILE)[0]
    key = encryption.gen_password_key(password, salt)
    encryption.encrypt_to_file(KEYS_FILE, json.dumps(keys), salt, key)

    click.echo(f"Successfully removed {name} from your keys.")
