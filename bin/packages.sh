#!/bin/bash -e

BASEDIR=`dirname $0`/..

echo "Building wheel..."
"$BASEDIR/env/bin/python" setup.py bdist_wheel

echo "Building egg..."
"$BASEDIR/env/bin/python" setup.py sdist

VERSION=`cat $BASEDIR/VERSION`
if [[ ${VERSION} =~ .*-RC[1-9]{1}[0-9]?$ ]]; then
        echo "Renaming release candidate package to: dcos-valkiria-${VERSION}.tar.gz"
        mv dist/dcos-valkiria-*.tar.gz dist/dcos-valkiria-${VERSION}.tar.gz
fi

