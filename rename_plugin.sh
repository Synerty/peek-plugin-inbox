#!/usr/bin/env bash


# remove the git index
[ -f .git/index ] && rm .git/index || true

rm -rf dist *egg-info || true

find ./ -name '__pycache__' -exec rm -rf {} \; || true

caps="ACTIVE_TASK"
underscore="_active_task"
hyphen="-active-task"
camelL="activeTask"
camelU="ActiveTask"

set nounset
set errexit

function replace {
    from=$1
    to=$2

    for d in `find ./ -type d`
    do
        new=`echo $d | sed "s/$from/$to/g"`
        [ "$d" != "$new" ] && mv $d $new
    done

    for f in `find ./ -type f`
    do
        new=`echo $f | sed "s/$from/$to/g"`
        [ "$f" != "$new" ] && mv $f $new
    done

    for f in `find ./ -type f -not -name '.git' -not -name 'rename_plugin.sh'`
    do
        sed -i "s/$from/$to/g" $f
    done

}

replace "_noop"  "$underscore"
replace "-noop" "$hyphen"
replace "NOOP" "$caps"
replace "Noop" "$camelU"
replace "noop" "$camelL"

# Remove compile generated javascript
find ./ -type f -not -name '.git' -name "*.js" -exec rm {} \; || true
find ./ -type f -not -name '.git' -name "*.js.map" -exec rm {} \; || true
