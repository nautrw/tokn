import click
import tokn.otp as otp
import pyotp
import tokn.encryption as encryption
import json
from math import floor

@click.group()
def cli():
    pass

@cli.command()
@click.argument('name', required=True)
def add(name: str):
    """Associate a secret key to the service NAME.
    
    NAME is the name of the service.
    """
    salt, encrypted = encryption.get_file_info("keys")
    password = click.prompt("Enter your password", hide_input=True).encode()
    key = encryption.gen_password_key(password, salt)
    decrypted = encryption.decrypt(encrypted, key)
    
    keys_dict = json.loads(decrypted)
    
    secret_key = click.prompt("Enter the secret key", hide_input=True)

    keys_dict[name] = secret_key
    
    encryption.encrypt_to_file("keys", json.dumps(keys_dict), salt, key)
    
    click.echo(f"Successfully added key to {name}")

@cli.command()
@click.argument('name', required=True)
def get(name: str):
    """Retrieve the TOTP code of the service NAME.
    
    NAME is the name of the service.
    """
    salt, encrypted = encryption.get_file_info("keys")
    password = click.prompt("Enter your password", hide_input=True).encode()
    key = encryption.gen_password_key(password, salt)
    decrypted = encryption.decrypt(encrypted, key)

    keys_dict = json.loads(decrypted)
    
    secret_key = keys_dict[name]
    
    totp = otp.generate_totp(secret_key)
    time_remaining = otp.get_time_remaining(secret_key)

    click.echo(f"Code: {totp}")
    click.echo(f"{floor(time_remaining)} seconds left")