import pytest
import tokn.otp as otp
import pyotp


def test_generate_otp():
    for i in range(10):
        key = pyotp.random_base32()
        totp = pyotp.TOTP(key)
        gen_key = otp.generate_totp(key)

        assert totp.verify(gen_key)
