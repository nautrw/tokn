from numpy import require
from tokn.util import require_password
import json
import click
import pyotp
from cryptography.fernet import InvalidToken
import os
import tokn.encryption as encryption
from tokn.encryption import KEYS_FILE
import tokn.otp as otp
from tokn.qr import read_qr_code


@click.command()
@click.option(
    "--code",
    is_flag=True,
    help="Enter the raw secret key code. Will ask for issuer and name.",
)
@click.option("--uri", is_flag=True, help="Enter a raw OTP URI.")
@require_password
def add(ctx: click.core.Context, code, uri):
    """Add a new account to the vault."""
    keys = ctx.obj["keys"]
    password = ctx.obj["password"]

    if code:
        issuer = click.prompt("Issuer of key")
        label = click.prompt("Account name")
        secret_key = click.prompt("Secret key", hide_input=True)

        clean_secret = secret_key.replace(" ", "").upper()
        if not otp.is_valid_secret(clean_secret):
            raise click.ClickException("Invalid secret key.")
    elif uri:
        uri = click.prompt("URI", hide_input=True)

        try:
            parsed_uri = pyotp.parse_uri(uri)
        except ValueError:
            raise click.ClickException("Invalid URI.")

        issuer = parsed_uri.issuer

        if not issuer:
            click.echo("URI is missing an issuer. Please enter one.")
            issuer = click.prompt("Issuer of key")

        label = parsed_uri.name
        secret_key = parsed_uri.secret
    else:
        qr_path = click.prompt("QR code image path")

        try:
            code = read_qr_code(qr_path)
        except ValueError:
            raise click.ClickException(
                "Could not extract QR code from image. "
                "Please ensure the image is valid."
            )

        try:
            parsed_uri = pyotp.parse_uri(code)
        except ValueError:
            raise click.ClickException("Invalid QR code.")

        issuer = parsed_uri.issuer
        if not issuer:
            click.echo("QR code is missing an issuer. Please enter one.")
            issuer = click.prompt("Issuer of key")

        label = parsed_uri.name
        secret_key = parsed_uri.secret

    click.echo(f"Issuer: {issuer}")
    click.echo(f"Label: {label}")

    click.confirm("Are you sure you want to add this account?", abort=True)

    new_key_obj = {"issuer": issuer, "label": label, "secret": secret_key}

    for i, key in enumerate(keys):
        if key["issuer"] == issuer and key["label"] == label:
            click.confirm("This key already exists. Override?", abort=True)

            keys[i] = new_key_obj
            break
    else:
        keys.append(new_key_obj)

    salt = encryption.get_file_info(KEYS_FILE)[0]
    key = encryption.gen_password_key(password.encode(), salt)
    encryption.encrypt_to_file(KEYS_FILE, json.dumps(keys), salt, key)

    click.echo(f'Successfully added key under issuer "{issuer}".')


@click.command()
@click.argument("issuer", required=True)
@click.argument("name", required=True)
@require_password
def remove(ctx: click.core.Context, issuer, label):
    """Remove an account NAME from the vault with issuer ISSUER."""
    keys = ctx.obj["keys"]
    password = ctx.obj["password"]

    issuers = set([entry["issuer"] for entry in keys])
    if issuer not in issuers:
        raise click.ClickException("That account is not in your vault.")

    for i, key in enumerate(keys):
        if key["issuer"] == issuer and key["label"] == label:
            del keys[i]

    click.confirm(
        "Are you sure you want to delete this account from your vault?"
        "This action can not be reversed.",
        abort=True,
    )

    salt = encryption.get_file_info(KEYS_FILE)[0]
    key = encryption.gen_password_key(password, salt)
    encryption.encrypt_to_file(KEYS_FILE, json.dumps(keys), salt, key)

    click.echo(f'Successfully removed account "{issuer}:{label}"' "from your vault.")


@click.command()
@require_password
def change_password(ctx: click.core.Context):
    """Change the password of the vault."""
    current_password = ctx.obj["password"]

    file = encryption.get_keys_with_password(KEYS_FILE, current_password)

    new_password = click.prompt("New password", hide_input=True)
    new_password_confirm = click.prompt("Confirm new password", hide_input=True)

    if new_password == new_password_confirm:
        new_salt = os.urandom(16)
        new_key = encryption.gen_password_key(new_password.encode(), new_salt)

        encryption.encrypt_to_file(KEYS_FILE, json.dumps(file), new_salt, new_key)

        click.echo("Successfully changed password.")
    else:
        raise click.ClickException("Passwords must be the same. Please try again.")
