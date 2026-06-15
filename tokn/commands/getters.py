from math import floor

import click
from cryptography.fernet import InvalidToken

import tokn.encryption as encryption
from tokn.encryption import KEYS_FILE
import tokn.otp as otp


@click.command()
@click.argument("issuer", required=True)
@click.pass_context
def get(ctx, issuer: str):
    """Retrieve TOTP codes of all accounts under the ISSUER.

    ISSUER is the name of the issuer.
    """
    keys = ctx.obj["keys"]

    issuers = set([entry["issuer"] for entry in keys])

    if issuer not in issuers:
        raise click.ClickException(f"No issuer {issuer} found.")

    accounts = [key for key in keys if key["issuer"] == issuer]

    for account in accounts:
        click.echo(f"- {account['label']}")
        secret_key = account["secret"]

        totp = otp.generate_totp(secret_key)
        time_remaining = otp.get_time_remaining(secret_key)
        next_code = otp.get_next_totp(secret_key)

        click.echo(f"   Code: {totp}")
        click.echo(f"   {floor(time_remaining)} seconds left")
        click.echo(f"   Next code: {next_code}")

@click.command()
@click.pass_context
def list(ctx):
    """List all the services in the keys file."""
    keys = ctx.obj["keys"]

    if not keys:
        click.echo("No keys found in keys file.")
    else:
        # no, defaultdict will not work and I don't know why
        entries = {}

        for key in keys:
            if key["issuer"] not in entries.keys():
                entries[key["issuer"]] = []

            entries[key["issuer"]].append(key["label"])

        for entry in entries:
            click.echo(entry)

            for label in entries[entry]:
                click.echo(f" - {label}")