#!/bin/bash -e

BASEDIR=`dirname $0`/..

cd $BASEDIR

PATH=$(pwd)/dist:$PATH

echo "Modifying version to: $1"
echo $1 > VERSION
sed -e "s/version = .*/version = '$1'/" dcos_valkiria/constants.py > tmp
mv tmp dcos_valkiria/constants.py
