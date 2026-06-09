from datetime import datetime
import pyotp
import time

def generate_totp(key):
    totp = pyotp.TOTP(key)
    
    return totp.now()
    

def get_time_remaining(key):
    totp = pyotp.TOTP(key)
    
    return totp.interval - datetime.now().timestamp() % totp.interval

def get_next_totp(key):
    totp = pyotp.TOTP(key)
    
    return totp.at(int(time.time()) + totp.interval)