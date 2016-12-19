#!/bin/bash -e

DIR=dist
BASEDIR=`dirname $0`/..

if [ -d "$DIR" ]; then
	VERSION=`cat $BASEDIR/VERSION`
	curl -u stratio:${NEXUSPASS} --upload-file dist/dcos-valkiria-${VERSION}.tar.gz http://sodio.stratio.com/nexus/content/sites/paas/dcos-valkiria/${VERSION}/
else
	echo "Run 'make package' first"
	exit 1
fi
