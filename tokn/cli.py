import click
from tokn.commands.write_commands import add, remove, change_password
from tokn.commands.getters import get, list, vault
from tokn.qr import read_qr_code


@click.group()
def cli():
    pass


commands = [
    add,
    remove,
    get,
    list,
    change_password,
    vault,
]
for command in commands:
    cli.add_command(command)
