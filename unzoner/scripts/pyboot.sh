#!/usr/bin/env bash

[[ -e /root/functions ]] && . /root/functions
[[ -e /dev/shm/.env ]] && . /dev/shm/.env

if [[ $DEBUG == '1' ]]; then env; fi

SOURCE_DIRS="${SOURCE_DIRS:-src app}"

cmd=${1}
shift

for dir in ${SOURCE_DIRS}; do
	if [[ -f $WORKDIR/$dir/$ARCH/$cmd.dist/$cmd ]]; then
		exec "${WORKDIR}/${dir}/${ARCH}/${cmd}.dist/${cmd}" "$@"
	fi

	if [[ -f $WORKDIR/$dir/$cmd.py ]]; then
		exec "$(which python)" "${WORKDIR}/${dir}/${cmd}.py" "$@"
	fi
done