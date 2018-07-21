#!/usr/bin/python3
import click
import subprocess

from secrets import token_urlsafe
from pathlib import Path
import os

echo = click.echo
PIPE = subprocess.PIPE

@click.group()
def cli():
    pass


warnings_to_ignore = [
    "WARNING: unsafe ownership",

]


@cli.command(name="mount-pass")
@click.option('--name', '-n', required=True,
              help="The name of the pass entry containing the VeraCrypt password")
@click.argument('partition', type=click.Path(exists=True))
@click.argument('mount-point', type=click.Path(exists=True))
def mount_using_pass(name, partition, mount_point):
    """
    Mount a VeraCrypt partition using a password stored in the app 'pass'
    Usage: mount-pass [-n, --name "entry_name] <partition> <mount_point>
    """
    pass_call = subprocess.run(['pass', name], stdout=PIPE, stderr=PIPE, universal_newlines=True)
    err = pass_call.stderr

    if err:
        if "WARNING: unsafe ownership" in err:
            echo("warning suppressed")
        else:
            echo(err)
            return

    err, password = get_password_from_pass(name)

    if err:
        echo(err)
        return

    cmd = ['veracrypt', "--text", "--non-interactive", "--password", password, partition, mount_point]
    echo("mounting...")
    vcmount_call = subprocess.run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    echo(vcmount_call.args)
    err = vcmount_call.stderr
    out = vcmount_call.stdout

    if err:
        echo("ERROR: {}".format(err))
        return err, out

    echo("SUCCESS: {}".format(out))

    return err, out


def get_password_from_pass(name):
    pass_call = subprocess.run(['pass', name], stdout=PIPE, stderr=PIPE, universal_newlines=True)
    err = pass_call.stderr

    if err:
        if "WARNING: unsafe ownership" in err:
            echo("warning suppressed")
        else:
            return err, None

    password = pass_call.stdout.strip()
    echo("password = {} len={}".format(password, len(password)))
    return None, pass_call.stdout.strip()


@cli.command("change-key")
@click.option("--old", "-o", help="The old password")
@click.option("--id", "-i", help="The  name or id of the pass entry")
@click.option("--new", "-n", required=True, help="The new password")
@click.option("--container", "-c", required=True, help="The unmounted container")
def change_vc_password(old, new, container, id):
    """
    Change the key (password) of a VeraCrypt container
    Must specify either the old password (-o), or the ID of a Pass entry (-i).
    If the ID is specified, Pass will be updated with the new entry
    """

    if old is None and id is None:
        err = "error: You must specify either the old password, or the id of a Pass entry"
        return err, None

    if id:
        old_password = get_password_from_pass(old)
    else:
        old_password = old

    entropy = token_urlsafe(300)
    file = Path.home() / "tmp" / "tmp-random.txt"
    file.parent.mkdir(parents=True, exist_ok=True)

    with open(file, 'w') as f:
        f.write(entropy)

    command = [
        'veracrypt',
        '-t', '-C', '--non-interactive',
        '--password', old_password,
        '--new-password', new,
        '--pim', '0',
        '--new-pim', '0',
        '--random-source', str(file),
        container
    ]

    vc_call = subprocess.run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

    err = vc_call.stderr
    out = vc_call.stdout

    if err:
        echo("ERROR {}".format(err))

    echo ("success: {}".format(out))
    return err, out





