from jinja2.utils import missing
from datetime import datetime
import pyotp
import time
import re
import base64
import binascii


def generate_totp(key):
    totp = pyotp.TOTP(key)

    return totp.now()


def get_time_remaining(key):
    totp = pyotp.TOTP(key)

    return totp.interval - datetime.now().timestamp() % totp.interval


def get_next_totp(key):
    totp = pyotp.TOTP(key)

    return totp.at(int(time.time()) + totp.interval)


def is_valid_secret(secret):
    clean = secret.strip().upper().replace(" ", "")
    missing_padding = len(secret) % 8
    if missing_padding != 0:
        clean += "=" * (8 - missing_padding)

    try:
        base64.b32decode(clean)
        return True
    except binascii.Error:
        return False
