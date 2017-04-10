#!/usr/bin/env bash

PY_PACKAGE="peek_plugin_active_task"
PIP_PACKAGE="peek-plugin-active-task"

set -o nounset
set -o errexit
#set -x

if [ -n "$(git status --porcelain)" ]; then
    echo "There are uncomitted changes, please make sure all changes are comitted" >&2
    exit 1
fi

if ! [ -f "setup.py" ]; then
    echo "setver.sh must be run in the directory where setup.py is" >&2
    exit 1
fi

VER="${1:?You must pass a version of the format 0.0.0 as the only argument}"

if git tag | grep -q "${VER}"; then
    echo "Git tag for version ${VER} already exists." >&2
    exit 1
#    read -p "Git tag for version ${VER} already exists, do you want to overwrite (Y/N) ? " -n 1 -r
#    echo    # (optional) move to a new line
#    if ! [[ $REPLY =~ ^[Yy]$ ]]; then
#        echo "Aborting, version already exists"
#        exit 1
#    fi
fi

echo "Setting version to $VER"

# Update the setup.py
sed -i "s;^package_version.*=.*;package_version = '${VER}';"  setup.py

# Update the package version
sed -i "s;.*version.*;__version__ = '${VER}';" ${PY_PACKAGE}/__init__.py

# Update the plugin_package.json
# "version": "#PLUGIN_VER#",
#sed -i 's;.*"version".*:.*".*;    "version":"'${VER}'",;' ${PACKAGE}/plugin-module/package.json
sed -i 's;.*"version".*:.*".*;    "version":"'${VER}'",;' ${PY_PACKAGE}/plugin_package.json

# Upload to test pypi
python setup.py sdist upload -r pypitest

# Reset the commit, we don't want versions in the commit
git commit -a -m "Updated to version ${VER}"

git tag ${VER}
git push
git push --tags

RELEASE_DIR=${RELEASE_DIR-/media/psf/release}
if [ -d  $RELEASE_DIR ]; then
    rm -rf $RELEASE_DIR/${PIP_PACKAGE}*.gz || true
    cp ./dist/${PIP_PACKAGE}-$VER.tar.gz $RELEASE_DIR
fi



echo "If you're happy with this you can now run :"
echo
echo "python setup.py sdist upload -r pypi"
echo