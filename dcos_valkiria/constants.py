version = '0.1.0-RC1'
valkiria_version = '0.1.0-RC1'
"""DCOS valkiria version"""
url_install = 'http://sodio.stratio.com/nexus/content/sites/paas/valkiria/{0}/valkiria-{0}.tar.gz'.format(valkiria_version)
url_list = 'http://127.0.0.1:9050/api/v1/list'
name = 'valkiria-{0}.tar.gz'.format(valkiria_version)
previous_path = 'root/workspace/Release/Infra/valkiria{0}/target/bin/valkiria'.format(valkiria_version)
end_path = '/opt/stratio/valkiria'
services_type = ['daemon', 'docker', 'service']
default_timeout = ['ConnectTimeout=10']
killed_message = 'TASK_KILLED'
task_not_found = 'TASK NOT FOUND'

