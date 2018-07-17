import click
echo = click.echo


@click.command()
@click.option('--name', default='World', help="any name")
@click.option('--count', type=int, default=1, help="number of times to be greeted")
@click.argument('output', type=click.File('w'), default='-', required=False)
def test(name, count, output):
    """
    A basic greeter script.
    Usage: hello [options] <output_file>
        Where <output_file> is the path to a file, or the string '-' for stdout.
    """

    for i in range(count):
        echo("Hello {}".format(name), file=output)
