#!/usr/bin/env bash

[ -e "/root/functions" ] && . /root/functions
[ -e "/dev/shm/.env" ] && . /dev/shm/.env

if [[ "${DEBUG}" == "1" ]]; then
    env
fi

dd_out=$(mktemp)
result=$(dd if=/dev/zero of=${dd_out} bs=8k count=50k 2>&1 | tail -n -1)
printf "${result}"
[ -f ${dd_out} ] && rm -rf ${dd_out}
