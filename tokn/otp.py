import pyotp


def generate_totp(key):
    totp = pyotp.TOTP(key)
    return totp.now()
