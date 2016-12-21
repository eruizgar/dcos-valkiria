'''Description:
    Administer and manage commands in DCOS cluster nodes.

Usage:
    dcos valkiria --info
    dcos valkiria install [--option SSHOPT=VAL ...]
            [--config-file=<path>]
            [--user=<user>]
            (--ips=<ip-or-hostname>)

Commands:
    install
        Establish an SSH connection to the master or agent nodes and install
        valkiria in the ip passed.

Options:
    -h, --help
        Show this screen.
    --info
        Show a short description of this subcommand.
    --option SSHOPT=VAL
        The SSH options. For information, enter `man ssh_config` in your
        terminal.
    --ips=<ip-or-hostname>
        List of ips when you want to install valkiria.
    --user=<user>
        The SSH user, where the default user [default: root].
    --version
        Print version information.
'''

import os
import subprocess

import docopt
from dcos import cmds, emitting, mesos, util
from dcos.errors import DCOSException, DefaultError
from dcos_valkiria import constants

logger = util.get_logger(__name__)
emitter = emitting.FlatEmitter()


def main():
    try:
        return _main()
    except DCOSException as e:
        emitter.publish(e)
        return 1


def _main():
    args = docopt.docopt(
        doc=__doc__,
        version="dcos-valkiria version {}".format(constants.version)
    )

    return cmds.execute(_cmds(), args)


def _cmds():
    """
    :returns: All of the supported commands
    :rtype: [Command]
    """

    return [
        cmds.Command(
            hierarchy=['valkiria', '--info'],
            arg_keys=[],
            function=_info),

        cmds.Command(
            hierarchy=['valkiria', 'install'],
            arg_keys=['--ips', '--user', '--option', '--config-file'],
            function=_install),
    ]


def _info():
    """Print node cli information.

    :returns: process return code
    :rtype: int
    """

    emitter.publish("Administer and manage commands in DCOS cluster nodes.")
    return 0


def _install(ips, user, option, config_file):
    """SSH into a DCOS node using the IP addresses to install valkiria
     :param ip: ip to connect
     :type ip: [str]
     :param option: SSH option
     :type option: [str]
     :param user: SSH user
     :type user: str | None
     :rtype: int
     :returns: process return code
     """
    ssh_options = util.get_ssh_options(config_file, option)
    if not ips:
        emitter.publish(DefaultError("--ips requires argument"))
        return 0
    ips = ips.split(" ")

    for ip in ips:
        cmd = '''ssh {2}{0}@{1} 'curl -O {3};
                tar -xvf {4}; cp {5} {6}; rm -rf root/; rm {4};
                nohup {6} a > valkiria.out 2> valkiria.log < /dev/null &' '''.format(
                user,
                ip,
                ssh_options,
                constants.url,
                constants.name,
                constants.previous_path,
                constants.end_path)
        emitter.publish(DefaultError("Running `{}`".format(cmd)))
        subprocess.call(cmd, shell=True)
    return 0


if __name__ == "__main__":
    main()
