import pyotp


def generate_totp(key):
    totp = pyotp.totp(key)  # ty:ignore[call-non-callable]
    return totp.now()
