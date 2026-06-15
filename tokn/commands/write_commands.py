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
@click.option("--code", is_flag=True)
@click.pass_context
def add(ctx, code):
    """Add a new secret key."""
    keys = ctx.obj["keys"]
    password = ctx.obj["password"]
    
    if code:
        issuer = click.prompt("Issuer of key")
        label = click.prompt("A label for this key")
        secret_key = click.prompt("Secret key", hide_input=True)
        
        clean_secret = secret_key.replace(" ", "").upper()
        if not otp.is_valid_secret(clean_secret):
            raise click.ClickException("Invalid secret key.")
    else:
        qr_path = click.prompt("Enter the path of the QR code image")
        
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
    
        click.echo(f"Issuer: {parsed_uri.issuer}")
        click.echo(f"Label: {parsed_uri.name}")
        click.confirm("Are you sure you want to add this key?", abort=True)
       
        issuer = parsed_uri.issuer
        label = parsed_uri.name
        secret_key = parsed_uri.secret
    
    keys.append({
        "issuer": issuer,
        "label": label,
        "secret": secret_key
    })

    salt = encryption.get_file_info(KEYS_FILE)[0]
    key = encryption.gen_password_key(password, salt)
    encryption.encrypt_to_file(KEYS_FILE, json.dumps(keys), salt, key)
    
    click.echo(f"Successfully added key under issuer {issuer}.")
    
@click.command()
@click.argument("issuer", required=True)
@click.argument("label", required=True)
@click.pass_context
def remove(ctx, issuer, label):
    """Remove a service NAME from the keys file."""
    keys = ctx.obj["keys"]
    password = ctx.obj["password"]
    
    issuers = set([entry["issuer"] for entry in keys])
    if issuer not in issuers:
        raise click.ClickException("That service is not in your keys file.")

    for i, key in enumerate(keys):
        if key["issuer"] == issuer and key["label"] == label:
            del keys[i]

    click.confirm(
        "Are you sure you want to delete this key? This action can not be reversed.",
        abort=True,
    )

    salt = encryption.get_file_info(KEYS_FILE)[0]
    key = encryption.gen_password_key(password, salt)
    encryption.encrypt_to_file(KEYS_FILE, json.dumps(keys), salt, key)

    click.echo(f"Successfully removed {issuer} from your keys.")

@click.command()
@click.pass_context
def change_password(ctx):
    """Change the password of the encrypted file."""
    current_password = ctx.obj["password"]

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