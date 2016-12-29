'''Description:
    Administer and manage commands in DCOS cluster nodes.

Usage:
    dcos valkiria --info
    dcos valkiria install [--option SSHOPT=VAL ...]
            [--config-file=<path>]
            [--user=<user>]
            (--ips=<ip-or-hostname>)
    dcos valkiria task [--option SSHOPT=VAL ...]
            [--config-file=<path>]
            [--user=<user>]
            (--ips=<ip-or-hostname>)

Commands:
    install
        Establish an SSH connection to the master or agent nodes and install
        valkiria in the ip passed.
    tasks
        Establish an SSH connection to the master or agent nodes and list
        the killables tasks.

Options:
    -h, --help
        Show this screen.
    --info
        Show a short description of this subcommand.
    --option SSHOPT=VAL
        The SSH options. For information, enter `man ssh_config` in your
        terminal.
    --ips=<ip-or-hostname>
        List of ips where you want to install valkiria.
    --user=<user>
        The SSH user, where the default user [default: root].
    --version
        Print version information.
'''
import json
import re
import subprocess
import docopt
from dcos import cmds, emitting, util
from dcos.errors import DCOSException, DefaultError
from dcos_valkiria import constants
from prettytable import PrettyTable

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

        cmds.Command(
            hierarchy=['valkiria', 'task'],
            arg_keys=['--ips', '--user', '--option', '--config-file'],
            function=_tasks),
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
     :param ips: ip to connect
     :type ips: [str]
     :param option: SSH option
     :type option: [str]
     :param user: SSH user
     :type user: str | None
     :rtype: int
     :returns: process return code
     """
    ssh_options = util.get_ssh_options(config_file, option)
    for ip in _get_ips_list(ips):
        cmd = '''ssh {2}{0}@{1} 'curl -O {3};
                tar -xvf {4}; if [ ! -d {6} ]; then mkdir -p {6};fi ;cp {5} {6}; rm -rf {7}; rm {4};
                nohup {6}/valkiria a > valkiria.out 2> valkiria.log < /dev/null &' '''.format(
            user,
            ip,
            ssh_options,
            constants.url_install,
            constants.name,
            constants.previous_path,
            constants.end_path,
            constants.previous_path.split('/')[0])
        emitter.publish(DefaultError("Running `{}`".format(cmd)))
        subprocess.call(cmd, shell=True)
    return 0


def _tasks(ips, user, option, config_file):
    """SSH into a DCOS node using the IP addresses found in master's
       state.json
     :param ips: ip to connect
     :type ips: [str]
     :param option: SSH option
     :type option: [str]
     :param user: SSH user
     :type user: str | None
     :rtype: int
     :returns: process return code
    """
    ssh_options = util.get_ssh_options(config_file, option)
    table = PrettyTable(['Ip', 'TaskId'])
    for ip in _get_ips_list(ips):
        cmd = '''ssh {2}{0}@{1} 'curl -sb -H {3}' '''.format(
            user,
            ip,
            ssh_options,
            constants.url_list)
        emitter.publish(DefaultError("Running `{}`".format(cmd)))
        try:
            resp = json.loads(subprocess.check_output(cmd, shell=True).decode('utf-8'))
            for service_type in constants.services_type:
                try:
                    xs = resp[service_type]
                    for x in xs:
                        if service_type == 'daemon':
                            table.add_row([ip, x['Name']])
                        elif service_type == 'service' or service_type == 'docker':
                            table.add_row([ip, x['TaskName']])
                        else:
                            table.add_row([ip, 'No {} tasks running'.format(service_type)])
                except KeyError:
                    emitter.publish(DefaultError("{0} not contain`{1}` tasks running".format(ip, service_type)))
        except subprocess.CalledProcessError:
            table.add_row([ip, 'IP not valid'])

    return table


def _get_ips_list(ips):
    """
    Convert argument ips in a iterable list of ips.
    :param ips: ip to connect
    :rtype: ips: list(str)
    """
    if not ips:
        emitter.publish(DefaultError("--ips requires argument"))
        return 1
    return re.findall(r'''\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b''', ips)


if __name__ == "__main__":
    main()