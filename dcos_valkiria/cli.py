'''Description:
    Administer and manage commands in DCOS cluster nodes.

Usage:
    dcos valkiria --info
    dcos valkiria ssh [--option SSHOPT=VAL ...]
             [--config-file=<path>]
             [--user=<user>]
             [--master-proxy]
             (--leader | --master | --mesos-id=<mesos-id> | --slave=<slave-id>)
             <command>

Commands:
    ssh
        Establish an SSH connection to the master or agent nodes and execute
        command.

Options:
    --config-file=<path>
        Path to SSH configuration file.
    -h, --help
        Show this screen.
    --info
        Show a short description of this subcommand.
   --leader
        The leading master.
    --master
        Deprecated. Please use --leader.
    --master-proxy
        Proxy the SSH connection through a master node. This can be useful when
        accessing DCOS from a separate network. For example, in the default AWS
        configuration, the private slaves are unreachable from the public
        internet. You can access them using this option, which will first hop
        from the publicly available master.
    --option SSHOPT=VAL
        The SSH options. For information, enter `man ssh_config` in your
        terminal.
    --slave=<agent-id>
        Agent node with the provided ID.
    --user=<user>
        The SSH user, where the default user [default: core].
    --version
        Print version information.

Positional Arguments:
    <command>
        Name of the DCOS package in the package repository.
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

    if args.get('--master'):
        raise DCOSException(
            '--master has been deprecated. Please use --leader.'
        )
    elif args.get('--slave'):
        raise DCOSException(
            '--slave has been deprecated. Please use --mesos-id.'
        )

    return cmds.execute(_cmds(), args)


def _cmds():
    """
    :returns: All of the supported commands
    :rtype: [Command]
    """

    return [
        cmds.Command(
            hierarchy=['command', '--info'],
            arg_keys=[],
            function=_info),

        cmds.Command(
            hierarchy=['command', 'ssh'],
            arg_keys=['--leader', '--mesos-id', '--option', '--config-file',
                      '--user', '--master-proxy', '<command>'],
            function=_ssh),
        cmds.Command(
            hierarchy=['command', 'service'],
            arg_keys=['--leader', '--mesos-id', '--option', '--config-file',
                      '--user', '--master-proxy', '<command>'],
            function=_ssh),

    ]


def _info():
    """Print node cli information.

    :returns: process return code
    :rtype: int
    """

    emitter.publish("Administer and manage commands in DCOS cluster nodes.")
    return 0


def _ssh(leader, slave, option, config_file, user, master_proxy, command):
    """SSH into a DCOS node using the IP addresses found in master's
       state.json

    :param leader: True if the user has opted to SSH into the leading
                   master
    :type leader: bool | None
    :param slave: The slave ID if the user has opted to SSH into a slave
    :type slave: str | None
    :param option: SSH option
    :type option: [str]
    :param config_file: SSH config file
    :type config_file: str | None
    :param user: SSH user
    :type user: str | None
    :param master_proxy: If True, SSH-hop from a master
    :type master_proxy: bool | None
    :param command: command executed on target
    :type command: str
    :rtype: int
    :returns: process return code
    """

    ssh_options = util.get_ssh_options(config_file, option)
    dcos_client = mesos.DCOSClient()

    if leader:
        host = mesos.MesosDNSClient().hosts('leader.mesos.')[0]['ip']
    else:
        summary = dcos_client.get_state_summary()
        slave_obj = next((slave_ for slave_ in summary['slaves']
                          if slave_['id'] == slave),
                         None)
        if slave_obj:
            host = mesos.parse_pid(slave_obj['pid'])[1]
        else:
            raise DCOSException('No slave found with ID [{}]'.format(slave))

    master_public_ip = dcos_client.metadata().get('PUBLIC_IPV4')
    if master_proxy:
        if not os.environ.get('SSH_AUTH_SOCK'):
            raise DCOSException(
                "There is no SSH_AUTH_SOCK env variable, which likely means "
                "you aren't running `ssh-agent`.  `dcos node ssh "
                "--master-proxy` depends on `ssh-agent` to safely use your "
                "private key to hop between nodes in your cluster.  Please "
                "run `ssh-agent`, then add your private key with `ssh-add`.")
        if not master_public_ip:
            raise DCOSException(("Cannot use --master-proxy.  Failed to find "
                                 "'PUBLIC_IPV4' at {}").format(
                                     dcos_client.get_dcos_url('metadata')))

        cmd = 'ssh -A -t {0}{1}@{2} ssh -A -t {1}@{3} {4}'.format(
            ssh_options,
            user,
            master_public_ip,
            host,
            command)
    else:
        cmd = 'ssh -t {0}{1}@{2} {3}'.format(
            ssh_options,
            user,
            host,
            command)

    emitter.publish(DefaultError("Running `{}`".format(cmd)))
    if (not master_proxy) and master_public_ip:
        emitter.publish(
            DefaultError("If you are running this command from a separate "
                         "network than DCOS, consider using `--master-proxy`"))

    return subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    main()
