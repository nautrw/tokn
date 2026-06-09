from datetime import datetime
import pyotp


def generate_totp(key):
    totp = pyotp.TOTP(key)
    
    return totp.now()
    

def get_time_remaining(key):
    totp = pyotp.TOTP(key)
    
    return totp.interval - datetime.now().timestamp() % totp.interval