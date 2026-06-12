import json
from ast import parse

import click
import pyotp
from cryptography.fernet import InvalidToken
from platformdirs import PlatformDirs

import tokn.encryption as encryption
import tokn.otp as otp
from tokn.qr import read_qr_code

dirs = PlatformDirs("tokn", "nautrw", ensure_exists=True)
KEYS_FILE = dirs.user_data_dir + "/keys"

@click.group()
@click.pass_context
def add(ctx):
    pass

@add.command()
def qr():
    password = click.prompt("Enter your password", hide_input=True).encode()

    try:                                                                     
        keys_dict = encryption.get_keys_with_password(KEYS_FILE, password)
    except InvalidToken:
        raise click.ClickException("Incorrect password.")
    
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
    
    if not otp.is_valid_secret(parsed_uri.secret):
        raise click.ClickException("Invalid secret key.")

    click.echo(f"Issuer: {parsed_uri.issuer}")
    click.echo(f"Label: {parsed_uri.name}")
    click.confirm("Are you sure you want to add this key?", abort=True)

    keys_dict.append({
        "issuer": parsed_uri.issuer,
        "label": parsed_uri.name,
        "secret": parsed_uri.secret
    })
    
    salt = encryption.get_file_info(KEYS_FILE)[0]
    key = encryption.gen_password_key(password, salt)
    encryption.encrypt_to_file(KEYS_FILE, json.dumps(keys_dict), salt, key)
    
    click.echo(f"Successfully added key under issuer {parsed_uri.issuer}.")

@add.command()
def code():
    password = click.prompt("Enter your password", hide_input=True).encode()

    try:                                                                     
        keys_dict = encryption.get_keys_with_password(KEYS_FILE, password)
    except InvalidToken:
        raise click.ClickException("Incorrect password.")

    issuer = click.prompt("Issuer of key")
    label = click.prompt("A label for this key")
    secret_key = click.prompt("Secret key", hide_input=True)
    
    clean_secret = secret_key.replace(" ", "").upper()
    if not otp.is_valid_secret(clean_secret):
        raise click.ClickException("Invalid secret key.")
   
    keys_dict.append({
        "issuer": issuer,
        "label": label,
        "secret": secret_key
    })
    
    salt = encryption.get_file_info(KEYS_FILE)[0]
    key = encryption.gen_password_key(password, salt)
    encryption.encrypt_to_file(KEYS_FILE, json.dumps(keys_dict), salt, key)
    
    click.echo(f"Successfully added key under issuer {issuer}.")
