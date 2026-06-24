from functools import update_wrapper
import click
from cryptography.fernet import InvalidToken
from tokn.encryption import KEYS_FILE
import os
import tokn.encryption as encryption

def require_password(func):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        if not os.path.isfile(KEYS_FILE):
            click.echo("New user detected. Starting setup.")

            new_password = click.prompt("New password", hide_input=True)
            password_confirm = click.prompt("Confirm new password", hide_input=True)

            if not new_password == password_confirm:
                raise click.ClickException("Passwords must be the same. Please try again.")

            random_salt = os.urandom(16)
            key = encryption.gen_password_key(new_password.encode(), random_salt)

            open(KEYS_FILE, "x")
            encryption.encrypt_to_file(KEYS_FILE, "[]", random_salt, key)

            click.echo(f'Successfully created new vault at path "{KEYS_FILE}".')
            
            ctx.obj = {
                "password": new_password,
                "keys": []
            }
        else:
            password = click.prompt("Enter your password", hide_input=True)

            try:
                keys = encryption.get_keys_with_password(KEYS_FILE, password.encode())
            except InvalidToken:
                raise click.ClickException("Incorrect password.")

            ctx.obj = {
                "password": password,
                "keys": keys
            }
        
        return ctx.invoke(func, ctx, *args, **kwargs)
    
    return update_wrapper(new_func, func)

def codes_formatted(current, next, time_remaining):
    if 0 <= time_remaining <= 10:
        time_color = 'red'
        current_color = 'reset'
        next_color = 'green'
    elif 11 <= time_remaining <= 15:
        time_color = 'yellow'
        current_color = 'green'
        next_color = 'reset'
    else:
        time_color = 'green'
        current_color = 'green'
        next_color = 'reset'
    
    current_formatted = click.style(current, fg=current_color)
    next_formatted = click.style(next, fg=next_color)
    time_formatted = click.style(f"{time_remaining}s", fg=time_color)
    
    return current_formatted, next_formatted, time_formatted