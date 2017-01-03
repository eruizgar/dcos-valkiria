"""Description:
    Administer and manage commands in DCOS cluster nodes.

Usage:
    dcos valkiria --info
    dcos valkiria install [--option SSHOPT=VAL ...]
            [--config-file=<path>]
            [--user=<user>]
            (--ips=<"ip-or-iplist">)
    dcos valkiria task [--option SSHOPT=VAL ...]
            [--config-file=<path>]
            [--user=<user>]
            (--ips=<"ip-or-iplist">)

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
    --ips=<"ip-or-iplist">
        Required: The ip list string in format "IP1,IP2..."
    --user=<user>
        The SSH user, where the default user [default: root].
    --version
        Print version information.
"""
import json
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
    print(str(ips))
    for ip in _get_ips_list(ips):
        cmd = '''ssh {2}{0}@{1} 'curl -sb -H {3}' '''.format(
            user,
            ip,
            ssh_options,
            constants.url_list)
        emitter.publish(DefaultError("Running `{}`".format(cmd)))
        try:
            resp = json.loads(subprocess.check_output(cmd, shell=True).decode('utf-8'))
            services_type_without_tasks = 0
            for service_type in constants.services_type:
                try:
                    xs = resp[service_type]
                    for x in xs:
                        if service_type == 'daemon':
                            table.add_row([ip, x['Name']])
                        elif service_type == 'service' or service_type == 'docker':
                            table.add_row([ip, x['TaskName']])
                except KeyError:
                    if services_type_without_tasks == 2:
                        table.add_row([ip, 'No tasks running'])
                    else:
                        services_type_without_tasks += 1
        except subprocess.CalledProcessError:
            table.add_row([ip, 'IP not valid'])
    return table


def _get_ips_list(ips):
    """
    Convert argument ips in a iterable list of ips.
    :param ips: ip to connect
    :rtype: ips: str
    """
    if not ips:
        emitter.publish(DefaultError("--ips requires argument"))
        return 1
    ip_list = ips.replace(" ", "").split(",")
    valid_ips = []
    for ip in ip_list:
        if _valid_ip_format(ip):
            valid_ips.append(ip)
        else:
            emitter.publish("[[{}]] is a not valid ip format.".format(ip))
    return valid_ips


def _valid_ip_format(addr):
    try:
        addr = addr.strip().split(".")
    except AttributeError:
        return False
    try:
        return len(addr) == 4 and all(octet.isdigit() and int(octet) < 256
                                      for octet in addr)
    except ValueError:
        return False


if __name__ == "__main__":
    main()
