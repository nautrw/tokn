import click
import tokn.otp as otp
import pyotp


@click.command()
def main():
    key = pyotp.random_base32()
    print(f"Generated totp: {otp.generate_totp(key)}")
