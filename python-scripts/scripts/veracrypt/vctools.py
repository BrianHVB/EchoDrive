#!/usr/bin/python3
import click
import subprocess
import pexpect

from secrets import token_urlsafe
from pathlib import Path
import os
import sys

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

    echo("success: {}".format(out))
    return err, out


@cli.command("set-pass")
@click.option("--name", "-n", required=True, help="The name/key of the entry")
@click.option("--password", "-p", required=True, help="The password")
def change_pass_password(name, password):
    # TOTO Add in error checking after expect()
    index = p.expect(['good', 'bad', pexpect.EOF, pexpect.TIMEOUT])
        # if index == 0:
        #     do_something()
        # elif index == 1:
        #     do_something_else()
        # elif index == 2:
        #     do_some_other_thing()
        # elif index == 3:
        #     do_something_completely_different()


    # LOG_OUTPUT = sys.stdout
    LOG_OUTPUT = None

    command = 'pass insert --force {}'.format(name)
    child = pexpect.spawn(command, encoding='utf-8', ignore_sighup=True, echo=False, logfile=LOG_OUTPUT)

    child.expect("Enter password")
    child.sendline(password)

    child.expect("Retype password")
    child.sendline(password)

    result = child.read()


    if 'error' in result.lower():
        err_msg = result.replace("\r\n", ' ')
        echo("ERROR: {}".format(err_msg))
        return err_msg, None


    verify_command = 'pass {}'.format(name)

    child = pexpect.spawn(verify_command, encoding='utf-8', ignore_sighup=True, echo=False, logfile=LOG_OUTPUT)
    child.expect(password)

    # print(child.readline())
    # print(child.exitstatus, child.signalstatus)

    # sub = subprocess.Popen(command, stdout=PIPE, stderr=PIPE, stdin=PIPE, universal_newlines=True, encoding='utf8', shell=True)
    # sub.stdin.write('\n')
    # sub.stdin.close()
    # err = sub.stderr
    # msg = sub.stdout
    # # echo("error: {}".format(err))
    # # echo("message: {}".format(msg))
    #
    # echo("error: {}".format(err.read()))
    # echo("message: {}".format(msg.read()))
    #
    # # sub.stdin.write("123\n")
    # # sub.stdin.flush()
    # # sub.stdin.close()
    # sub.wait(timeout=3)


    # if "password for {k}".format(k=key) in message:
    #     err, msg = sub.communicate(password)
    #     echo("pass password change")
    #     echo("error: {}".format(err))
    #     echo("success: {}".format(msg))




def set_pass_password(entry_name, password):

    """
    Trying to automate setting new password for the Unix pass program.

    When using a terminal, the flow looks like this:

        $ pass insert --force gmail
        >> Enter password for gmail: <type in password using masked prompt>
        >> Retype password for gmail: <reenter password>


    What I would like my function to do:
        1. Run the command `pass insert --force {entry_name}`
        2. Capture the output (and echo it for testing)
        3. Check output for the presence of 'password for gmail', and if True
            3A. write '{password}\n' to stdin
            3B. write '{password}\n' to stdin again
        4. Echo any errors or messages for testing

    Issues:
        I'm stuck on step 2. The subprocess either hangs indefinitely, times out wth an error, or produces no output

    Attempts:
        I've tried configurations of Popen(), using both stdin.write() and communicate(). I've set wait() calls at
        various points.I've tried both the shell=True, and shell=False (preferred for security) options

    """
    from subprocess import Popen, PIPE

    command = ['pass', 'insert', '--force', entry_name]

    sub = Popen(command, stdout=PIPE, stderr=PIPE, stdin=PIPE, universal_newlines=True)

    sub.stdin.write('123\r')
    sub.stdin.write('123\r')

    # msg1, err1 = sub.communicate()
    # msg2 = sub.stdout
    # err2 = sub.stderr


    # At this point I assume that the command has run, and that there is an "Enter password..." message
    # print(msg2, err2.read())
    # print(message) # never happens, because process hangs on stdout.read()
    #
    # if 'password for {}'.format(entry_name) in message:
    #     err, msg = sub.communicate(input='{p}\n{p}\n'.format(p=password))
    #     print('errors: {}\nmessage: {}'.format(err, msg))



def set_pass_password2(entry_name, password):
    import sys
    from pexpect.popen_spawn import PopenSpawn

    command = 'pass insert --force {k}'.format(k=entry_name)
    # child = pexpect.spawn(command, encoding='utf-8', ignore_sighup=True)
    child = PopenSpawn(command, encoding='utf-8')
    child.logfile=sys.stdout
    print(child.read())
    # child.expect("Enter password")
    child.sendline(password)
    # child.expect("Retype password")
    print(child.read())
    child.sendline(password + 'a')
    print(child.readline())
    print(child.exitstatus, child.signalstatus)
