#!/bin/bash

set -o nounset
set -o 
set -x

PLUGIN_NAME='plugin_active_task'

function convertBambooDate() {
# EG s="2010-01-01T01:00:00.000+01:00"
# TO 100101.0100
python <<EOF
from dateutil.parser import parse
print parse("${BAMBOO_DATE}").strftime('%y%m%d.%H%M')
EOF
}
echo "start version is $VER"

BUILD="${BUILD}"
VER="${VER}"
DATE="`convertBambooDate`"

if [ "${VER}" == '${bamboo.jira.version}' ]; then
    VER="b${DATE}"
fi

echo "New version is $VER"
echo "New build is $BUILD"

TAR_DIR="${PLUGIN_NAME}_$VER#$BUILD"
DIR="deploy/$TAR_DIR"
mkdir -p $DIR/cpython

echo "New version is $VER"


# Source
cp -pr ${PLUGIN_NAME}/alembic $DIR/cpython
cp -pr ${PLUGIN_NAME}/src/${PLUGIN_NAME} $DIR/cpython
cp -pr ${PLUGIN_NAME}/plugin_changelog.json $DIR
cp -pr ${PLUGIN_NAME}/plugin_version.json $DIR


find $DIR -iname .git -exec rm -rf {} \; || true
find $DIR -iname "test" -exec rm -rf {} \; 2> /dev/null || true
find $DIR -iname "tests" -exec rm -rf {} \; 2> /dev/null || true
find $DIR -iname "*test.py" -exec rm -rf {} \; || true
find $DIR -iname "*tests.py" -exec rm -rf {} \; || true
find $DIR -iname ".Apple*" -exec rm -rf {} \; || true
find $DIR -iname "*TODO*" -exec rm -rf {} \; || true
find $DIR -iname ".idea" -exec rm -rf {} \; || true


# Apply version number

for f in `grep -l -r  '#PLUGIN_VER#' .`; do
    echo "Updating version in file $f"
    sed -i "s/#PLUGIN_VER#/$VER/g" $f
done

for f in `grep -l -r  '#PLUGIN_BUILD#' .`; do
    echo "Updating build in file $f"
    sed -i "s/#PLUGIN_BUILD#/$BUILD/g" $f
done

for f in `grep -l -r  '#BUILD_DATE#' .`; do
    echo "Updating date in file $f"
    sed -i "s/#BUILD_DATE#/$DATE/g" $f
done

###########################################
# PYPY WAS SLOWER THAN CPYTHON
# Using a simple task, all the dispatching took far longer with pypy
# pypy 5.6 was tried, and it was lef for a while, it just didn't optimise that part
# While it may optimise computationally expensive tasks, it probably won't help Peek
###########################################

## Copy cpython source to pypy
#cp -pr $DIR/cpython $DIR/pypy

pushd $DIR/cpython
echo "Compiling all cpython python modules"
python -m compileall -f .

echo "Deleting just cpython source files"
find . -name "*.py" -exec rm {} \;
popd


## PYPY doesn't accept compiled files with out source
## The worker should never perform an upgrade
#echo "Removing non worker source files"
#pushd $DIR/pypy
#rm -rf $PLUGIN_NAME/agent
#rm -rf $PLUGIN_NAME/client_fe
#rm -rf $PLUGIN_NAME/server_fe
#rm -rf alembic
#popd



tar cjf ${TAR_DIR}.tar.bz2 -C deploy $TAR_DIR
