import click
import subprocess

echo = click.echo
PIPE = subprocess.PIPE

@click.group()
def cli():
    pass


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
    echo("error: {}\nvalue: {}".format(pass_call.stderr.strip(), pass_call.stdout.strip()))
    password = pass_call.stdout
    echo(password)
