#!/bin/bash -e

BASEDIR=`dirname $0`/..

cd $BASEDIR

PATH=$(pwd)/dist:$PATH
$BASEDIR/env/bin/nosetests --with-coverage --cover-package=dcos_valkiria --cover-xml ../../tests/integration
