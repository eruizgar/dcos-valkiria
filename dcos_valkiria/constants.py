version = '0.1.0-SNAPSHOT'
"""DCOS valkiria version"""
url_install = 'http://sodio.stratio.com/nexus/content/sites/paas/valkiria/0.1.0-SNAPSHOT/valkiria-0.1.0-SNAPSHOT.tar.gz'
url_list = 'http://127.0.0.1:9050/api/v1/list'
name = 'valkiria-0.1.0-SNAPSHOT.tar.gz'
previous_path = 'root/workspace/valkiriamaster/target/bin/valkiria'
end_path = '/opt/stratio/valkiria'
services_type = ['daemon', 'docker', 'service']
default_timeout = ['ConnectTimeout=10']
killed_message = 'TASK_KILLED'
task_not_found = 'TASK NOT FOUND'

