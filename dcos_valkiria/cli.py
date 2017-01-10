"""Description:
    Administer and manage commands in DCOS cluster nodes.

Usage:
    dcos valkiria --info
    dcos valkiria install [--option SSHOPT=VAL ...]
            [--config-file=<path>]
            [--user=<user>]
            (--ips=<"ip-or-iplist">)
    dcos valkiria uninstall [--option SSHOPT=VAL ...]
            [--config-file=<path>]
            [--user=<user>]
            (--ips=<"ip-or-iplist">)
    dcos valkiria task [--option SSHOPT=VAL ...]
            [--config-file=<path>]
            [--user=<user>]
            (--ips=<"ip-or-iplist">)
    dcos valkiria kill [--option SSHOPT=VAL ...]
            [--config-file=<path>]
            [--user=<user>]
            (--ip=<ip-or-hostname>)
            (--task-id=<task-id>)
    dcos valkiria start [--option SSHOPT=VAL ...]
            [--config-file=<path>]
            [--user=<user>]
            (--ips=<"ip-or-iplist">)
    dcos valkiria stop [--option SSHOPT=VAL ...]
            [--config-file=<path>]
            [--user=<user>]
            (--ips=<"ip-or-iplist">)
    dcos valkiria status [--option SSHOPT=VAL ...]
            [--config-file=<path>]
            [--user=<user>]
            (--ips=<"ip-or-iplist">)

Commands:
    install
        Establish an SSH connection to the master or agent nodes and install Valkiria on them.
    uninstall
        Establish an SSH connection to the master or agent nodes and uninstall Valkiria on them
    tasks
        Establish an SSH connection to the master or agent nodes and list the killables tasks.
    kill
        Establish an SSH connection to the master or agent nodes and kill the task with a specific taskId.
    start
        Establish an SSH connection to the master or agent nodes and start the Valkiria agent process on them.
    stop
        Establish an SSH connection to the master or agent nodes and stop the Valkiria agent process on them.
    status
        Establish an SSH connection to the master or agent nodes and get the status of the Valkiria agent process on them.


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
    --ip=<ip-or-hostname>
        The ip where you want to kill the task
    --task-id=<task-id>
        The id of the task that you want to kill.
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
            hierarchy=['valkiria', 'uninstall'],
            arg_keys=['--ips', '--user', '--option', '--config-file'],
            function=_uninstall),

        cmds.Command(
            hierarchy=['valkiria', 'task'],
            arg_keys=['--ips', '--user', '--option', '--config-file'],
            function=_tasks),

        cmds.Command(
            hierarchy=['valkiria', 'kill'],
            arg_keys=['--ip', '--user', '--option', '--config-file', '--task-id'],
            function=_kill),

        cmds.Command(
            hierarchy=['valkiria', 'start'],
            arg_keys=['--ips', '--user', '--option', '--config-file'],
            function=_start),

        cmds.Command(
            hierarchy=['valkiria', 'stop'],
            arg_keys=['--ips', '--user', '--option', '--config-file'],
            function=_stop),

        cmds.Command(
            hierarchy=['valkiria', 'status'],
            arg_keys=['--ips', '--user', '--option', '--config-file'],
            function=_status),
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
    option = _set_default_timeout(option)
    ssh_options = util.get_ssh_options(config_file, option)
    for ip in _get_ips_list(ips):
        cmd = '''ssh {2}{0}@{1} ' if [ ! -d {6} ]; then
                curl -O {3}; tar -xvf {4};
                mkdir -p {6}; cp {5} {6}; rm -rf {7}; rm {4};
                nohup {6}/valkiria a 2> valkiria.log > /dev/null 2>&1 &
                echo $! > valkiria.pid
                else
                echo Valkiria is already installed in {1}
                fi ' '''.format(
            user,
            ip,
            ssh_options,
            constants.url_install,
            constants.name,
            constants.previous_path,
            constants.end_path,
            constants.previous_path.split('/')[0])
        subprocess.call(cmd, shell=True)
    return 0


def _uninstall(ips, user, option, config_file):
    """SSH into a DCOS node using the IP addresses to uninstall valkiria
     :param ips: ip to connect
     :type ips: [str]
     :param option: SSH option
     :type option: [str]
     :param user: SSH user
     :type user: str | None
     :rtype: int
     :returns: process return code
     """

    for ip in _get_ips_list(ips):
        # _stop(ip, user, option, config_file)
        option = _set_default_timeout(option)
        ssh_options = util.get_ssh_options(config_file, option)
        cmd = '''ssh {2}{0}@{1} ' if [ -d {6} ]; then
                if [ -f ./valkiria.pid ]; then pkill -F valkiria.pid; rm -rf valkiria.pid;
                fi
                rm -rf {6}; rm ./valkiria.log;
                fi ' '''.format(
            user,
            ip,
            ssh_options,
            constants.url_install,
            constants.name,
            constants.previous_path,
            constants.end_path)
        subprocess.call(cmd, shell=True)
    return 0


def _start(ips, user, option, config_file):
    """SSH into a DCOS node using the IP addresses to start valkiria agent
       :param ips: ip to connect
       :type ips: [str]
       :param option: SSH option
       :type option: [str]
       :param user: SSH user
       :type user: str | None
       :rtype: int
       :returns: process return code
       """
    option = _set_default_timeout(option)
    ssh_options = util.get_ssh_options(config_file, option)
    for ip in _get_ips_list(ips):
        cmd = '''ssh {2}{0}@{1} 'if [ ! -f ./valkiria.pid ]; then
            nohup {3}/valkiria a 2> valkiria.log > /dev/null 2>&1 &
            echo $! > valkiria.pid
            else
            echo Valkiria is currently running in {1}
            fi' '''.format(
            user,
            ip,
            ssh_options,
            constants.end_path)
        subprocess.call(cmd, shell=True)
    return 0


def _stop(ips, user, option, config_file):
    """SSH into a DCOS node using the IP addresses to stop valkiria agent
       :param ips: ip to connect
       :type ips: [str]
       :param option: SSH option
       :type option: [str]
       :param user: SSH user
       :type user: str | None
       :rtype: int
       :returns: process return code
       """
    option = _set_default_timeout(option)
    ssh_options = util.get_ssh_options(config_file, option)
    for ip in _get_ips_list(ips):
        cmd = '''ssh {2}{0}@{1} 'if [ -f ./valkiria.pid ]; then pkill -F valkiria.pid; rm -rf valkiria.pid;
            else
                echo Valkiria is currently not running in {1}.
            fi' '''.format(
            user,
            ip,
            ssh_options)
        subprocess.call(cmd, shell=True)
    return 0


def _status(ips, user, option, config_file):
    """SSH into a DCOS node using the IP addresses to check valkiria agent status
       :param ips: ip to connect
       :type ips: [str]
       :param option: SSH option
       :type option: [str]
       :param user: SSH user
       :type user: str | None
       :rtype: int
       :returns: process return code
       """
    option = _set_default_timeout(option)
    ssh_options = util.get_ssh_options(config_file, option)
    for ip in _get_ips_list(ips):
        cmd = '''ssh {2}{0}@{1} 'if [ ! -f ./valkiria.pid ]; then
            echo Valkiria is currently stopped in {1}
            else
            echo Valkiria is currently running in {1}
            fi' '''.format(
            user,
            ip,
            ssh_options,
            constants.end_path)
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
    option = _set_default_timeout(option)
    ssh_options = util.get_ssh_options(config_file, option)
    table = PrettyTable(['Ip', 'TaskId'])
    for ip in _get_ips_list(ips):
        cmd = '''ssh {2}{0}@{1} 'curl -sb -H {3}' '''.format(
            user,
            ip,
            ssh_options,
            constants.url_list)
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


def _kill(ip, user, option, config_file, task_id):
    """SSH into a DCOS node using the IP addresses found in master's
       state.json
     :param ip: ip to connect
     :type ip: [str]
     :param option: SSH option
     :type option: [str]
     :param user: SSH user
     :type user: str | None
     :rtype: int
     :returns: process return code
    """
    option = _set_default_timeout(option)
    ssh_options = util.get_ssh_options(config_file, option)
    table = PrettyTable(header=False)
    kill_options = "'{" + ''' "name":"{0}","killExecutor":0,"serviceType":0 '''.format(task_id).replace("\"",
                                                                                                        "\\\"") + "}'"
    if _valid_ip_format(ip):
        cmd = '''ssh {2}{0}@{1} "curl  -sb -H -X POST -d {3} http://127.0.0.1:9050/api/v1/valkiria " '''.format(
            user,
            ip,
            ssh_options,
            kill_options)
        try:
            resp = json.loads(subprocess.check_output(cmd, shell=True).decode('utf-8'))
            if resp['status'] == 'Success':
                table.add_row([ip, task_id, constants.killed_message, resp['process'][0]['ChaosTimeStamp']])
            elif task_id == '':
                emitter.publish(DefaultError("--task-id requires argument"))
                return 1
            else:
                table.add_row([ip, task_id, constants.task_not_found, '----'])
        except subprocess.CalledProcessError:
            emitter.publish(DefaultError('There is no such IP in the cluster'))
            return 1
        return table
    else:
        emitter.publish("[[{}]] invalid ip format.".format(ip))


def _set_default_timeout(option):
    if not option:
        return constants.default_timeout


def _get_ips_list(ips):
    """
    Convert argument ips in a iterable list of ips.
    :param ips: ip to connect
    :rtype: ips: str
    """
    try:
        ip_list = ips.replace(" ", "").split(",")
        valid_ips = []
        for ip in ip_list:
            if _valid_ip_format(ip):
                valid_ips.append(ip)
            elif ip == '':
                emitter.publish(DefaultError("--ips requires argument"))
            else:
                emitter.publish("[[{}]] invalid ip format.".format(ip))
        return valid_ips
    except AttributeError:
        emitter.publish(DefaultError("--ips requires argument"))
        return 1


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
